"""Cliente mínimo de API-Football (v3.football.api-sports.io).

Cada respuesta cruda se puede volcar a data/ vía store.save_snapshot desde el CLI.

⚠️ Validado 2026-06-13: el **plan Free NO accede a la season 2026** (solo 2022-2024) — las
llamadas al Mundial 2026 devuelven el error "Free plans do not have access to this season".
Estos endpoints solo sirven con plan pago. Además `injuries` no está cubierto para el Mundial
ni pagando. Mientras tanto, la fuente del torneo es FIFA (sources/fifa_fantasy.py). Ver docs/03.
Free tier: ~100 requests/día — cachear agresivo y no refrescar lo que no cambia.
"""

import time

import requests

from ..config import API_FOOTBALL_KEY, API_FOOTBALL_LEAGUE_ID, SEASON

BASE_URL = "https://v3.football.api-sports.io"

# Free tier: ~10 requests/min. Espaciamos las llamadas para no chocar el rate limit (429).
MIN_INTERVAL = 7.0
_last_request = 0.0


class ApiFootballError(RuntimeError):
    pass


def _get(endpoint: str, **params) -> dict:
    global _last_request
    if not API_FOOTBALL_KEY:
        raise ApiFootballError("Falta API_FOOTBALL_KEY en .env (plantilla en .env.example)")

    for attempt in range(4):
        wait = MIN_INTERVAL - (time.monotonic() - _last_request)
        if wait > 0:
            time.sleep(wait)
        resp = requests.get(
            f"{BASE_URL}/{endpoint}",
            headers={"x-apisports-key": API_FOOTBALL_KEY},
            params=params,
            timeout=30,
        )
        _last_request = time.monotonic()
        if resp.status_code == 429:  # rate limited → backoff y reintento
            time.sleep(10 * (attempt + 1))
            continue
        break

    resp.raise_for_status()
    body = resp.json()
    if body.get("errors"):
        raise ApiFootballError(f"{endpoint}: {body['errors']}")
    return body


def status() -> dict:
    """Estado de la cuenta: plan, requests usados hoy. No consume cuota."""
    return _get("status")


def fixtures() -> dict:
    """Calendario completo del Mundial (P2, P6)."""
    return _get("fixtures", league=API_FOOTBALL_LEAGUE_ID, season=SEASON)


def injuries() -> dict:
    """Lesionados/sancionados (P1). ⚠️ NO cubierto para el Mundial (injuries=False) — devolverá
    vacío. La señal de disponibilidad sale del pool de FIFA (status/matchStatus). Ver docs/03."""
    return _get("injuries", league=API_FOOTBALL_LEAGUE_ID, season=SEASON)


def players(page: int = 1) -> dict:
    """Stats por jugador del torneo (P3, P7, P8). Paginado."""
    return _get("players", league=API_FOOTBALL_LEAGUE_ID, season=SEASON, page=page)


def odds(fixture_id: int) -> dict:
    """Cuotas por fixture (P2, P4)."""
    return _get("odds", fixture=fixture_id)


# --- Histórico accesible en el free tier (2022-2024): priors de baja confianza (P3/P7/P8) ---

def wc2022_teams() -> dict:
    """Las 32 selecciones del Mundial 2022 con sus team-ids (1 request). Mapa nación→id."""
    return _get("teams", league=API_FOOTBALL_LEAGUE_ID, season=2022)


def team_player_stats(team_id: int, season: int = 2022, page: int = 1) -> dict:
    """Stats por jugador de una selección en una temporada histórica (acotado por equipo)."""
    return _get("players", team=team_id, league=API_FOOTBALL_LEAGUE_ID, season=season, page=page)
