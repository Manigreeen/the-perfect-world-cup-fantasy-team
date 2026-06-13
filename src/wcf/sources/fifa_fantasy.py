"""Endpoints del fantasy de play.fifa.com — ÚNICA fuente de ownership, precios y posición
del juego (P5, P9). Ver docs/03-fuentes-de-datos.md §3.

Descubiertos 2026-06-12: son JSON estáticos públicos, SIN auth. Otros nombres probados
(fixtures, settings, constants, ...) devuelven 403 — solo estos tres están abiertos:

  players.json  → pool completo: precio, posición del juego, % selected (total y por ronda),
                  puntos, form, status, squadId
  squads.json   → las 48 selecciones: id, nombre, grupo, isEliminated
  rounds.json   → las 8 rondas con fechas exactas (deadlines reales) y fixtures con
                  estadio, horario, marcador y status por partido
"""

import requests

BASE_URL = "https://play.fifa.com/json/fantasy"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def _get(name: str) -> list | dict:
    resp = requests.get(f"{BASE_URL}/{name}.json", headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_players() -> list:
    """Pool completo (~1500 jugadores): precio, posición, percentSelected, puntos."""
    return _get("players")


def fetch_squads() -> list:
    """Las 48 selecciones con grupo y flag de eliminación."""
    return _get("squads")


def fetch_rounds() -> list:
    """Las 8 rondas: fechas (deadline = startDate de la ronda) y fixtures con status."""
    return _get("rounds")
