"""Priors históricos (Mundial 2022) como señal de respaldo de BAJA confianza para P3/P7/P8 —
el único hueco que FIFA no cubre (volumen estadístico: tiros, key passes, tackles).

Diseño acordado con Mani:
  • Acotado: solo selecciones VIVAS relevantes para la ronda vigente (no las ~1500 del pool).
    Evoluciona solo: al eliminarse equipos, salen del set; los ya bajados quedan cacheados.
  • Inmutable y cacheado: el histórico no cambia → se baja una vez por selección a
    data/historical/2022/ y no se vuelve a pedir.
  • Peso bajo y decayente: es un prior suave. El rendimiento 2026 en vivo lo sobrescribe conforme
    pasan las rondas (ver strategy.HIST_PRIOR_STRENGTH y strategy.blend_rate). Un jugador pudo
    cambiar de nivel desde 2022; el prior no debe dominar la "plantilla óptima".

Quota: free tier 100 req/día. El fetch es resumible: corre `wcf history` los días que haga falta;
lo cacheado se salta.
"""

import json
import unicodedata
from pathlib import Path

from . import pool
from .config import DATA_DIR
from .sources import api_football

HIST_DIR = DATA_DIR / "historical" / "2022"
TEAM_MAP_PATH = DATA_DIR / "historical" / "team_ids_2022.json"
MIN_MINUTES = 90  # bajo este umbral el prior es ruido; se descarta

# Selecciones cuyo nombre en FIFA difiere del de API-Football en el WC2022 (y SÍ jugaron 2022).
NATION_ALIASES = {"Korea Republic": "South Korea", "IR Iran": "Iran"}


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in text if not unicodedata.combining(c)).lower().strip()


# --- Mapa nación → team-id del WC2022 (1 request, cacheado) ---

def team_id_map() -> dict[str, int]:
    if TEAM_MAP_PATH.is_file():
        return json.loads(TEAM_MAP_PATH.read_text(encoding="utf-8"))
    body = api_football.wc2022_teams()
    mapping = {t["team"]["name"]: t["team"]["id"] for t in body["response"]}
    TEAM_MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
    TEAM_MAP_PATH.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    return mapping


# --- Set relevante: selecciones vivas (no eliminadas) presentes en el histórico 2022 ---

def relevant_alive_nations() -> list[str]:
    """Nombres de selecciones vivas según el snapshot de FIFA. Acota y evoluciona el fetch."""
    squads = pool.load_squads()
    return sorted(s["name"] for s in squads.values() if not s.get("isEliminated"))


def _team_cache_path(team_id: int) -> Path:
    return HIST_DIR / f"team-{team_id}.json"


def cached_team_ids() -> set[int]:
    if not HIST_DIR.exists():
        return set()
    return {int(p.stem.split("-")[1]) for p in HIST_DIR.glob("team-*.json")}


def _fetch_team(team_id: int, nation: str) -> int:
    """Baja todas las páginas de una selección y cachea crudo. Devuelve nº de requests usados."""
    page, total, players, used = 1, 1, [], 0
    while page <= total:
        body = api_football.team_player_stats(team_id, season=2022, page=page)
        used += 1
        players.extend(body["response"])
        total = body["paging"]["total"]
        page += 1
    HIST_DIR.mkdir(parents=True, exist_ok=True)
    _team_cache_path(team_id).write_text(
        json.dumps({"nation": nation, "team_id": team_id, "players": players},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    return used


def run_fetch(max_requests: int = 80) -> dict:
    """Baja los priors de las selecciones vivas aún no cacheadas, respetando el tope de quota.

    Devuelve un resumen {fetched, skipped_cached, missing_from_2022, requests_used, stopped_early}.
    """
    mapping = team_id_map()
    alive = relevant_alive_nations()
    cached = cached_team_ids()

    fetched, missing, used, stopped = [], [], 1, False  # used=1 por el mapa si se bajó recién
    used = 0  # team_id_map ya cachea; no contamos su request acá para simplificar el tope
    for nation in alive:
        team_id = mapping.get(NATION_ALIASES.get(nation, nation))
        if team_id is None:
            missing.append(nation)  # no jugó el WC2022 → prior por defecto (posición)
            continue
        if team_id in cached:
            continue
        if used + 2 > max_requests:  # margen: una selección son ~1-2 páginas
            stopped = True
            break
        used += _fetch_team(team_id, nation)
        fetched.append(nation)
    return {
        "fetched": fetched,
        "skipped_cached": len(cached),
        "missing_from_2022": missing,
        "requests_used": used,
        "stopped_early": stopped,
    }


# --- Cálculo de priors por-90 a partir del crudo cacheado ---

def _rate(value, minutes) -> float:
    return round((value or 0) / minutes * 90, 3) if minutes else 0.0


def build_priors() -> dict[tuple[str, str], dict]:
    """Indexa priors por (nación_norm, apellido_norm) desde todo lo cacheado.

    Cada prior: tasas por-90 de tiros, key passes, tackles, tarjetas e involucramiento en gol,
    más la inicial del nombre para desambiguar y los minutos de muestra (confianza).
    """
    index: dict[tuple[str, str], list[dict]] = {}
    if not HIST_DIR.exists():
        return {}
    for path in HIST_DIR.glob("team-*.json"):
        doc = json.loads(path.read_text(encoding="utf-8"))
        nation = doc["nation"]
        for entry in doc["players"]:
            p, st = entry["player"], entry["statistics"][0]
            minutes = st["games"]["minutes"] or 0
            if minutes < MIN_MINUTES:
                continue
            last = p.get("lastname") or p["name"].split()[-1]
            first = p.get("firstname") or p["name"].split()[0]
            prior = {
                "first_initial": _norm(first)[:1],
                "minutes": minutes,
                "shots90": _rate(st["shots"]["total"], minutes),
                "key_passes90": _rate(st["passes"]["key"], minutes),
                "tackles90": _rate(st["tackles"]["total"], minutes),
                "cards90": _rate((st["cards"]["yellow"] or 0) + (st["cards"]["red"] or 0), minutes),
                "goal_involvement90": _rate((st["goals"]["total"] or 0) + (st["goals"]["assists"] or 0), minutes),
            }
            # Indexa bajo el apellido completo Y cada token (apellidos compuestos: "Mbappé Lottin"
            # matchea con el "Mbappé" de FIFA). Tokens de ≤2 letras se ignoran (ruido).
            for key in _surname_keys(last):
                index.setdefault((_norm(nation), key), []).append(prior)
    return index


def _surname_keys(last_name: str) -> set[str]:
    keys = {_norm(last_name)}
    keys.update(_norm(tok) for tok in last_name.split() if len(tok) > 2)
    return keys - {""}


def prior_for(first_name: str, last_name: str, nation: str, index: dict) -> dict | None:
    """Match por (nación, apellido) con fallback a tokens, desempatado por inicial del nombre."""
    nat = _norm(nation)
    candidates, seen = [], set()
    for key in _surname_keys(last_name):
        for c in index.get((nat, key), []):
            if id(c) not in seen:
                seen.add(id(c))
                candidates.append(c)
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    initial = _norm(first_name)[:1]
    exact = [c for c in candidates if c["first_initial"] == initial]
    return exact[0] if exact else max(candidates, key=lambda c: c["minutes"])
