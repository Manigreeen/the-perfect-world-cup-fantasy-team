"""Configuración central: paths, secretos y constantes del torneo (docs/01-reglas.md)."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"
OUTPUTS_DIR = ROOT / "outputs"

load_dotenv(ROOT / ".env")

API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "")

# API-Football: el Mundial es la liga id=1 ("World Cup"). Validar cobertura 2026 en Fase 1.
API_FOOTBALL_LEAGUE_ID = 1
SEASON = 2026

# --- Reglas oficiales ---

BUDGET_GROUPS = 100.0
BUDGET_KNOCKOUT = 105.0  # +$5M al abrir el Round of 32

SQUAD_COMPOSITION = {"GK": 2, "DEF": 5, "MID": 5, "FWD": 3}  # 15 jugadores
VALID_FORMATIONS = [
    (4, 4, 2), (4, 3, 3), (4, 5, 1),
    (3, 4, 3), (3, 5, 2),
    (5, 4, 1), (5, 3, 2),
]

# Máx. jugadores por selección, por fase. Ojo: R32 sigue en 3 pese al reset.
MAX_PER_COUNTRY = {"MD1": 3, "MD2": 3, "MD3": 3, "R32": 3, "R16": 4, "QF": 5, "SF": 6, "F": 8}

# Transfers libres antes de cada ronda. None = ilimitadas. Rollover de 1 solo en grupos.
FREE_TRANSFERS = {"MD2": 2, "MD3": 2, "R32": None, "R16": 4, "QF": 4, "SF": 5, "F": 6}
TRANSFER_HIT = -3  # por transfer sobre la asignación

# Lockout de transfers = kickoff del primer partido de la ronda (startDate en rounds.json
# de play.fifa.com, verificado 2026-06-12). La fuente viva es `wcf rounds`.
DEADLINES = {
    "MD2": "2026-06-18T17:00:00+01:00",
    "MD3": "2026-06-24T20:00:00+01:00",
    "R32": "2026-06-28T20:00:00+01:00",
    "R16": "2026-07-04T18:00:00+01:00",
    "QF": "2026-07-09T21:00:00+01:00",
    "SF": "2026-07-14T20:00:00+01:00",
    "F": "2026-07-18T22:00:00+01:00",
}
