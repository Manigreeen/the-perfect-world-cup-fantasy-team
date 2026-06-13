"""Cliente mínimo de API-Football (v3.football.api-sports.io).

Cada respuesta cruda se puede volcar a data/ vía store.save_snapshot desde el CLI.
Free tier: ~100 requests/día — cachear agresivo y no refrescar lo que no cambia.
"""

import requests

from ..config import API_FOOTBALL_KEY, API_FOOTBALL_LEAGUE_ID, SEASON

BASE_URL = "https://v3.football.api-sports.io"


class ApiFootballError(RuntimeError):
    pass


def _get(endpoint: str, **params) -> dict:
    if not API_FOOTBALL_KEY:
        raise ApiFootballError("Falta API_FOOTBALL_KEY en .env (plantilla en .env.example)")
    resp = requests.get(
        f"{BASE_URL}/{endpoint}",
        headers={"x-apisports-key": API_FOOTBALL_KEY},
        params=params,
        timeout=30,
    )
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
    """Lesionados/sancionados del torneo (P1). Validar cobertura en selecciones."""
    return _get("injuries", league=API_FOOTBALL_LEAGUE_ID, season=SEASON)


def players(page: int = 1) -> dict:
    """Stats por jugador del torneo (P3, P7, P8). Paginado."""
    return _get("players", league=API_FOOTBALL_LEAGUE_ID, season=SEASON, page=page)


def odds(fixture_id: int) -> dict:
    """Cuotas por fixture (P2, P4)."""
    return _get("odds", fixture=fixture_id)
