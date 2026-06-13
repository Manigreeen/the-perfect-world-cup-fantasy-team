"""Parsea data/my-team.md y lo valida contra el último snapshot del pool de FIFA.

Atrapa errores de transcripción antes de que contaminen recomendaciones: precio mal anotado,
posición distinta a la LISTADA en el juego, país equivocado, y violaciones de squad
(composición 2/5/5/3, máx 3 por país en grupos, presupuesto $100M).
"""

import re
import unicodedata

from . import store
from .config import BUDGET_GROUPS, DATA_DIR, SQUAD_COMPOSITION

MY_TEAM_PATH = DATA_DIR / "my-team.md"
PRICE_TOLERANCE = 0.05


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c)).lower().strip()


def parse_my_team() -> list[dict]:
    """Filas de la tabla del squad que ya tienen jugador anotado."""
    rows = []
    for line in MY_TEAM_PATH.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 6 and cells[0].isdigit() and cells[1]:
            match = re.search(r"(\d+(?:\.\d+)?)", cells[4])
            rows.append({
                "n": int(cells[0]),
                "name": cells[1],
                "country": cells[2],
                "pos": cells[3].upper(),
                "price": float(match.group(1)) if match else None,
                "role": cells[5],
            })
    return rows


def find_player(row: dict, players: list[dict], squad_names: dict[int, str]) -> dict | None:
    """Match por nombre normalizado (full name o knownName); desempata por selección."""
    target = _norm(row["name"])
    exact, partial = [], []
    for p in players:
        full = _norm(f"{p['firstName']} {p['lastName']}")
        known = _norm(p["knownName"]) if p.get("knownName") else None
        if target in (full, known):
            exact.append(p)
        elif _norm(p["lastName"]) == target.split()[-1]:
            partial.append(p)
    candidates = exact or partial
    if len(candidates) > 1:
        same_country = [p for p in candidates
                        if _norm(squad_names.get(p["squadId"], "")) == _norm(row["country"])]
        candidates = same_country or candidates
    return candidates[0] if candidates else None


def validate() -> list[str]:
    """Lista de líneas de reporte; lanza FileNotFoundError si no hay snapshot del pool."""
    latest_players = store.load_latest("fifa_players")
    latest_squads = store.load_latest("fifa_squads")
    if not latest_players or not latest_squads:
        raise FileNotFoundError("No hay snapshot del pool — corre `wcf pool` primero")
    captured_at, players = latest_players
    squad_names = {s["id"]: s["name"] for s in latest_squads[1]}

    rows = parse_my_team()
    lines = [f"Validando contra snapshot del pool de {captured_at}", ""]
    total_price, country_count, pos_count = 0.0, {}, {}

    for row in rows:
        p = find_player(row, players, squad_names)
        if p is None:
            lines.append(f"✗ #{row['n']} {row['name']}: NO encontrado en el pool (¿typo?)")
            continue
        issues = []
        real_country = squad_names.get(p["squadId"], "?")
        if _norm(real_country) != _norm(row["country"]):
            issues.append(f"selección es {real_country}, no {row['country']}")
        # pos y precio son opcionales en la plantilla: vacíos no es error, solo se
        # verifican si están anotados (los oficiales salen siempre en la línea ✓)
        if row["pos"] and p["position"] != row["pos"]:
            issues.append(f"el juego lo lista {p['position']}, no {row['pos']}")
        if row["price"] is not None and abs(p["price"] - row["price"]) > PRICE_TOLERANCE:
            issues.append(f"precio oficial ${p['price']}M, anotado {row['price']}")
        if p["status"] != "playing":
            issues.append(f"status '{p['status']}' en el juego")

        total_price += p["price"]
        country_count[real_country] = country_count.get(real_country, 0) + 1
        pos_count[p["position"]] = pos_count.get(p["position"], 0) + 1

        full_name = p.get("knownName") or f"{p['firstName']} {p['lastName']}"
        mark = "✓" if not issues else "⚠"
        detail = f" — {'; '.join(issues)}" if issues else ""
        lines.append(f"{mark} #{row['n']} {full_name} ({real_country}, {p['position']}, "
                     f"${p['price']}M, own {p['percentSelected']}%){detail}")

    lines.append("")
    lines.append(f"Anotados: {len(rows)}/15 · costo ${total_price:.1f}M "
                 f"(presupuesto ${BUDGET_GROUPS:.0f}M → quedan ${BUDGET_GROUPS - total_price:.1f}M)")
    titulares = sum(1 for r in rows if r["role"].lower().startswith("titular"))
    banca = sum(1 for r in rows if r["role"].lower().startswith("banca"))
    if titulares > 11:
        lines.append(f"⚠ {titulares} titulares anotados, el XI son 11")
    if banca > 4:
        lines.append(f"⚠ {banca} en banca, máximo 4 suplentes")
    for pos, want in SQUAD_COMPOSITION.items():
        have = pos_count.get(pos, 0)
        if have > want:
            lines.append(f"⚠ {pos}: {have} anotados, máximo {want}")
    for country, n in sorted(country_count.items(), key=lambda kv: -kv[1]):
        if n > 3:
            lines.append(f"⚠ {country}: {n} jugadores, máximo 3 en fase de grupos")
    return lines
