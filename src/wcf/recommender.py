"""Recomendador de transfers v0: dado mi squad, la proyección y las transfers libres, propone el
mejor par salir/entrar — o recomienda plantarse si nada supera el umbral del dial de riesgo.

Greedy (una transfer a la vez, la de mayor ganancia neta) sujeto a las restricciones reales:
misma posición (mantiene 2/5/5/3), presupuesto, y máx. jugadores por país de la fase. El óptimo
combinatorio global llega en Fase 4 (ILP); para 2-6 transfers el greedy alcanza y es legible.

Filosofía anti-nerviosismo (docs/05): el umbral `transfer_free_gain` del riesgo evita cambios que
no aportan; "plantarse y guardar la transfer" es una recomendación válida.
"""

from collections import Counter

from . import myteam, pool, projection, strategy
from .config import BUDGET_GROUPS, MAX_PER_COUNTRY


def _reason(in_row: dict, out_row: dict) -> str:
    bits = []
    comp = in_row["components"]
    if comp["matchup"] >= 1.05:
        bits.append("matchup favorable")
    elif comp["matchup"] <= 0.95:
        bits.append("matchup duro (aun así gana)")
    if in_row["ownership"] < 5:
        bits.append(f"diferencial {in_row['ownership']}%")
    if in_row["scouting"] > 0:
        bits.append("opta a scouting +2")
    if in_row["price"] < out_row["price"]:
        bits.append(f"libera ${round(out_row['price'] - in_row['price'], 1)}M")
    return ", ".join(bits) or "mayor proyección"


def recommend(risk: strategy.RiskProfile, free_transfers: int = 2, phase: str = "MD2") -> dict:
    ranked = projection.rank_pool(risk)
    by_id = {r["id"]: r for r in ranked["rows"]}

    squad_names = {sid: s["name"] for sid, s in pool.load_squads().items()}
    _, players = pool.load_players()
    my_squad = []
    for row in myteam.parse_my_team():
        p = myteam.find_player(row, players, squad_names)
        if not p:
            continue
        r = by_id.get(p["id"])
        my_squad.append({
            "id": p["id"], "squad_id": p["squadId"],
            "name": p.get("knownName") or f"{p['firstName']} {p['lastName']}",
            "pos": p["position"], "price": p["price"],
            "nation": squad_names.get(p["squadId"], ""),
            "proj": r["proj"] if r else 0.0,  # 0 si su selección no juega esta ronda
            "components": r["components"] if r else None, "ownership": r["ownership"] if r else None,
            "scouting": r["scouting"] if r else 0,
        })

    bank = BUDGET_GROUPS - sum(s["price"] for s in my_squad)
    country = Counter(s["nation"] for s in my_squad)
    my_ids = {s["id"] for s in my_squad}
    cap = MAX_PER_COUNTRY.get(phase, 3)

    candidates: dict[str, list] = {}
    for r in ranked["rows"]:
        if r["id"] not in my_ids:
            candidates.setdefault(r["pos"], []).append(r)

    swaps, threshold = [], risk.transfer_free_gain
    for _ in range(free_transfers):
        best = None
        for out_p in my_squad:
            for in_p in candidates.get(out_p["pos"], []):
                if in_p["price"] > out_p["price"] + bank:
                    continue
                if in_p["nation"] != out_p["nation"] and country[in_p["nation"]] + 1 > cap:
                    continue
                gain = in_p["proj"] - out_p["proj"]
                if gain >= threshold and (best is None or gain > best[0]):
                    best = (gain, out_p, in_p)
        if not best:
            break
        gain, out_p, in_p = best
        swaps.append({"out": out_p, "in": in_p, "gain": round(gain, 2), "why": _reason(in_p, out_p)})
        bank += out_p["price"] - in_p["price"]
        country[out_p["nation"]] -= 1
        country[in_p["nation"]] += 1
        my_ids.discard(out_p["id"])
        my_ids.add(in_p["id"])
        my_squad = [s for s in my_squad if s["id"] != out_p["id"]] + [{
            "id": in_p["id"], "squad_id": in_p["squad_id"], "name": in_p["name"],
            "pos": in_p["pos"], "price": in_p["price"], "nation": in_p["nation"],
            "proj": in_p["proj"], "components": in_p["components"],
            "ownership": in_p["ownership"], "scouting": in_p["scouting"],
        }]
        candidates[in_p["pos"]] = [c for c in candidates[in_p["pos"]] if c["id"] != in_p["id"]]

    return {"round": ranked["round"], "captured_at": ranked["captured_at"], "swaps": swaps,
            "bank": round(bank, 1), "threshold": threshold, "free_transfers": free_transfers,
            "total_gain": round(sum(s["gain"] for s in swaps), 2), "squad": my_squad}
