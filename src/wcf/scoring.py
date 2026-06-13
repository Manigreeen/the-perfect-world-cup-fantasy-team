"""Tabla oficial de puntos (docs/01-reglas.md §8).

La posición que manda es la LISTADA EN EL JUEGO (GK/DEF/MID/FWD), no la real en cancha.
"""

# Todos los jugadores
COMMON = {
    "appearance": 1,        # aparecer (hasta 60 min)
    "appearance_60": 1,     # adicional por jugar 60+
    "assist": 3,
    "yellow_card": -1,
    "red_card": -2,
    "own_goal": -2,
    "penalty_won": 2,
    "penalty_conceded": -1,
}

# Por posición
GOAL = {"GK": 9, "DEF": 7, "MID": 6, "FWD": 5}
CLEAN_SHEET = {"GK": 5, "DEF": 5, "MID": 1, "FWD": 0}  # requiere 60+ min
GOAL_CONCEDED_AFTER_FIRST = {"GK": -1, "DEF": -1, "MID": 0, "FWD": 0}  # el 1.er gol es gratis

PENALTY_SAVE = 3            # GK, no aplica en tandas
PER_3_SAVES = 1             # GK
PER_3_TACKLES = 1           # MID
PER_2_CHANCES_CREATED = 1   # MID
PER_2_SHOTS_ON_TARGET = 1   # FWD

# Bonus
DIRECT_FREE_KICK_GOAL_BONUS = 1
SCOUTING_BONUS = 2          # si pts del partido > 4 y ownership global < 5%
SCOUTING_MIN_POINTS = 5     # "más de 4" = 5 o más
SCOUTING_MAX_OWNERSHIP = 0.05
