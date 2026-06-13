"""Parámetros de estrategia del loop de optimización (decididos en docs/05).

El **apetito de riesgo es un dial ajustable**, no una constante: cambia los umbrales de cuándo el
recomendador sugiere una transfer, pagar el hit −3 o romper la capitanía, y cuánto premia el
ownership bajo (scouting bonus). Default: 'moderate'.

Override sin tocar código:
  - variable de entorno  WCF_RISK=aggressive   (en .env)
  - flag del CLI         wcf <cmd> --risk conservative   (cuando el comando lo exponga)
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from .config import ROOT

load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class RiskProfile:
    """Umbrales de decisión. Todos en puntos esperados sobre el horizonte del bloque."""
    name: str
    transfer_free_gain: float    # mínimo que el entrante supera al saliente para una transfer libre
    transfer_hit_gain: float     # mínimo para justificar pagar el hit −3 (cubre el costo con margen)
    captain_switch_gain: float   # mínimo para romper el plan de capitanía
    ownership_bonus_weight: float  # cuánto pesa el scouting bonus (<5%) en el ranking (1.0 = nominal)


# Tres niveles del dial. 'moderate' es el punto de partida; se recalibra con el backtest de MD2.
RISK_PROFILES = {
    "conservative": RiskProfile("conservative", 3.0, 5.0, 2.5, 0.5),
    "moderate":     RiskProfile("moderate",     2.0, 4.0, 1.5, 1.0),
    "aggressive":   RiskProfile("aggressive",   1.0, 3.5, 1.0, 1.5),
}

DEFAULT_RISK = "moderate"

# Horizonte: lookahead por bloque. Peso de cada ronda futura al proyectar profitability
# (próximo MD a peso pleno, el siguiente a la mitad). El R32 reinicia el bloque (knockout).
HORIZON_WEIGHTS = (1.0, 0.5)


def active_profile(override: str | None = None) -> RiskProfile:
    """Resuelve el perfil de riesgo: override del CLI > WCF_RISK del entorno > default."""
    name = (override or os.getenv("WCF_RISK") or DEFAULT_RISK).lower()
    if name not in RISK_PROFILES:
        valid = ", ".join(RISK_PROFILES)
        raise ValueError(f"riesgo '{name}' inválido — usa uno de: {valid}")
    return RISK_PROFILES[name]
