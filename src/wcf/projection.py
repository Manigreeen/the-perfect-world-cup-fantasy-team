"""Proyección v0 de puntos esperados por jugador para la próxima ronda, y ranking de profitability.

Enfoque **top-down** (apropiado para un torneo corto, ver docs/05): se parte de la salida fantasy
que da FIFA (avgPoints/form) y se la ancla con un prior por precio cuando hay poca muestra; luego
se ajusta por disponibilidad (P1) y dificultad de matchup (P2/P4). El prior histórico (P7) entra
como un pequeño término de volumen vía el scoring oficial, con peso bajo (decisión de Mani).

⚠️ Coeficientes v0 = heurística calibrable. Se recalibran con los puntos reales tras MD1/MD2
(ver el loop de calibración en docs/05). Hoy, con MD1 en curso, la proyección se apoya sobre todo
en el prior por precio; gana señal viva con cada ronda.
"""

import statistics
from collections import defaultdict

from . import historical, pool, strategy
from .scoring import SCOUTING_MAX_OWNERSHIP

# --- Constantes v0 (calibrar) ---
PRICE_TO_PPG = 0.60        # prior: un jugador de $10.5M ≈ 6.3 pts/partido esperados
PRIOR_STRENGTH = 2.0       # el prior por precio pesa como ~2 partidos de evidencia
MATCHUP_ALPHA = 0.08       # sensibilidad del ajuste por fuerza relativa (z-scores)
MATCHUP_CLAMP = (0.75, 1.25)
SHOT_ON_RATIO = 0.35       # fracción de tiros que van al arco (aprox., para el término de volumen)
HIST_VOLUME_WEIGHT = 0.30  # peso bajo del término de volumen histórico (P7)
SCOUT_PROJ_THRESHOLD = 4.0  # proyección mínima para esperar el scouting bonus (P5)


def team_strength(players: list[dict]) -> dict[int, float]:
    """Proxy de fuerza de selección: precio promedio de su top-15 (squads más caros = mejores)."""
    by_team: dict[int, list[float]] = defaultdict(list)
    for p in players:
        if p["status"] == "playing":
            by_team[p["squadId"]].append(p["price"])
    return {sid: statistics.fmean(sorted(prices, reverse=True)[:15])
            for sid, prices in by_team.items() if prices}


def games_played(player: dict) -> int:
    rp = player["stats"].get("roundPoints")
    return len(rp) if isinstance(rp, dict) else 0


def availability(player: dict) -> float:
    """P(juega) v0 desde los flags de FIFA. transferred=fuera; not_in_squad=muy bajo."""
    if player["status"] != "playing":
        return 0.0
    return {"start": 1.0, "sub": 0.55, "not_in_squad": 0.1}.get(player.get("matchStatus"), 0.85)


def base_ppg(player: dict) -> float:
    """Puntos/partido base: mezcla la salida observada de FIFA (avgPoints) con el prior por precio,
    con shrinkage según partidos jugados. Poca muestra → manda el precio; más rondas → manda lo visto."""
    prior = player["price"] * PRICE_TO_PPG
    observed = player["stats"].get("avgPoints") or 0.0
    g = games_played(player)
    return (PRIOR_STRENGTH * prior + g * observed) / (PRIOR_STRENGTH + g)


def _zscores(strength: dict[int, float]) -> dict[int, float]:
    vals = list(strength.values())
    mean, sd = statistics.fmean(vals), (statistics.pstdev(vals) or 1.0)
    return {sid: (v - mean) / sd for sid, v in strength.items()}


def matchup_factor(squad_id: int, opp_id: int | None, z: dict[int, float]) -> float:
    """Ajuste por fuerza relativa: rival más débil → >1, más fuerte → <1, acotado ±25%."""
    if opp_id is None or squad_id not in z or opp_id not in z:
        return 1.0
    diff = z[squad_id] - z[opp_id]
    lo, hi = MATCHUP_CLAMP
    return max(lo, min(hi, 1.0 + MATCHUP_ALPHA * diff))


def volume_points(player: dict, prior: dict | None) -> float:
    """Puntos de volumen esperados (P7) desde el prior histórico, vía el scoring oficial.
    FWD: +1 cada 2 tiros al arco · MID: +1 cada 2 chances (key passes) y +1 cada 3 tackles."""
    if not prior:
        return 0.0
    pos = player["position"]
    if pos == "FWD":
        return prior["shots90"] * SHOT_ON_RATIO / 2
    if pos == "MID":
        return prior["key_passes90"] / 2 + prior["tackles90"] / 3
    return 0.0


def project(player: dict, z: dict[int, float], fixture: dict | None, prior: dict | None) -> dict:
    """Puntos esperados del jugador para la próxima ronda, con sus componentes (transparencia)."""
    opp = fixture["opponent_id"] if fixture else None
    base = base_ppg(player)
    avail = availability(player)
    mf = matchup_factor(player["squadId"], opp, z)
    vol = HIST_VOLUME_WEIGHT * volume_points(player, prior)
    proj = (base * mf + vol) * avail
    return {"proj": round(proj, 2), "base": round(base, 2), "matchup": round(mf, 2),
            "avail": avail, "volume": round(vol, 2)}


def expected_scouting(player: dict, proj: float, risk: strategy.RiskProfile) -> float:
    """Bonus de scouting esperado (P5): +2 si <5% owned y rinde; ponderado por el dial de riesgo."""
    if player["percentSelected"] < SCOUTING_MAX_OWNERSHIP * 100 and proj >= SCOUT_PROJ_THRESHOLD:
        return risk.ownership_bonus_weight * 1.0
    return 0.0


def rank_pool(risk: strategy.RiskProfile) -> dict:
    """Proyecta y rankea a los jugadores disponibles de las selecciones que juegan la próxima ronda."""
    captured_at, players = pool.load_players()
    squads = pool.load_squads()
    rounds = pool.load_rounds()
    target = pool.upcoming_round(rounds)
    z = _zscores(team_strength(players))
    prior_index = historical.build_priors()
    squad_names = {sid: s["name"] for sid, s in squads.items()}

    rows = []
    for p in players:
        squad = squads.get(p["squadId"])
        if not squad or squad.get("isEliminated") or p["status"] != "playing":
            continue
        fixture = pool.squad_fixture(target, p["squadId"])
        if not fixture:  # su selección no juega esta ronda
            continue
        nation = squad_names.get(p["squadId"], "")
        prior = historical.prior_for(p["firstName"], p["lastName"], nation, prior_index)
        proj = project(p, z, fixture, prior)
        scout = expected_scouting(p, proj["proj"], risk)
        total = proj["proj"] + scout
        rows.append({
            "id": p["id"],
            "name": p.get("knownName") or f"{p['firstName']} {p['lastName']}",
            "pos": p["position"], "nation": nation, "price": p["price"],
            "ownership": p["percentSelected"],
            "proj": total, "value": round(total / p["price"], 3) if p["price"] else 0,
            "scouting": round(scout, 2), "components": proj, "has_prior": prior is not None,
        })
    rows.sort(key=lambda r: r["proj"], reverse=True)
    return {"round": target, "captured_at": captured_at, "rows": rows}
