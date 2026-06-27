"""Optimizador ILP del squad (Fase 4): arma los 15 óptimos desde cero para el reset del R32.

A diferencia del recomendador greedy (`recommender.py`, bueno para 1-2 transfers en grupos), acá
se resuelve el problema combinatorio completo con PuLP. Es la herramienta correcta cuando hay
**transfers ilimitadas + presupuesto nuevo** (el "gran reset" del knockout): elegir 15 jugadores y
su XI a la vez, no cambios de a pares.

Modelo de dos niveles (clave): se optimiza la proyección del **XI titular + doblete del capitán**,
NO la suma de los 15. La banca son rellenos baratos válidos. Así el budget se gasta en los que
juegan, no en suplentes caros.

  maximizar  Σ projᵢ·yᵢ  +  Σ projᵢ·cᵢ        (yᵢ=titular, cᵢ=capitán → su proj cuenta doble)
  sujeto a   composición 2/5/5/3 del squad (xᵢ) · presupuesto · máx N por país
             yᵢ ≤ xᵢ · Σyᵢ=11 · formación válida (GK=1, DEF 3-5, MID 3-5, FWD 1-3)
             Σcᵢ=1 · cᵢ ≤ yᵢ

⚠️ El óptimo es solo tan bueno como la proyección v0 que lo alimenta (`projection.py`). Optimiza
perfecto sobre números estimados; recalibrar pesos mejora más que afinar el solver.
"""

import pulp

from . import pool, projection, report, strategy
from .config import (BUDGET_GROUPS, BUDGET_KNOCKOUT, MAX_PER_COUNTRY, OUTPUTS_DIR,
                     ROUND_LABELS, SQUAD_COMPOSITION)

# Rango de titulares por posición. Equivale exactamente a las 7 formaciones válidas de config
# (toda combinación DEF∈[3,5], MID∈[3,5], FWD∈[1,3] con DEF+MID+FWD=10 es una formación legal).
STARTER_RANGE = {"GK": (1, 1), "DEF": (3, 5), "MID": (3, 5), "FWD": (1, 3)}


def solve(rows: list[dict], budget: float, max_per_country: int) -> list[dict] | None:
    """Resuelve el ILP sobre `rows` (candidatos ya proyectados). Devuelve los 15 elegidos, o None
    si el problema es infactible (p. ej. el pool aún es parcial y no alcanza para 15 con el cap)."""
    if not rows:
        return None
    R = {r["id"]: r for r in rows}
    ids = list(R)

    prob = pulp.LpProblem("wcf_squad", pulp.LpMaximize)
    x = {i: pulp.LpVariable(f"x_{i}", cat="Binary") for i in ids}  # en el squad de 15
    y = {i: pulp.LpVariable(f"y_{i}", cat="Binary") for i in ids}  # titular (XI)
    c = {i: pulp.LpVariable(f"c_{i}", cat="Binary") for i in ids}  # capitán

    prob += (pulp.lpSum(R[i]["proj"] * y[i] for i in ids)
             + pulp.lpSum(R[i]["proj"] * c[i] for i in ids))

    for pos, n in SQUAD_COMPOSITION.items():
        prob += pulp.lpSum(x[i] for i in ids if R[i]["pos"] == pos) == n
    prob += pulp.lpSum(R[i]["price"] * x[i] for i in ids) <= budget
    for nat in {R[i]["nation"] for i in ids}:
        prob += pulp.lpSum(x[i] for i in ids if R[i]["nation"] == nat) <= max_per_country

    for i in ids:
        prob += y[i] <= x[i]
        prob += c[i] <= y[i]
    prob += pulp.lpSum(y[i] for i in ids) == 11
    prob += pulp.lpSum(c[i] for i in ids) == 1
    for pos, (lo, hi) in STARTER_RANGE.items():
        starters = pulp.lpSum(y[i] for i in ids if R[i]["pos"] == pos)
        prob += starters >= lo
        prob += starters <= hi

    status = prob.solve(pulp.PULP_CBC_CMD(msg=0))
    if pulp.LpStatus[status] != "Optimal":
        return None
    return [R[i] for i in ids if x[i].value() and x[i].value() > 0.5]


def optimize(risk: strategy.RiskProfile, budget: float | None = None) -> dict:
    """Optimiza el squad de la próxima ronda de punta a punta y arma XI/capitán/banca reusando
    `report.select_xi` (consistencia con el reporte normal)."""
    ranked = projection.rank_pool(risk)
    target = ranked["round"]
    label = ROUND_LABELS.get(target["id"], f"R{target['id']}")
    if budget is None:
        budget = BUDGET_KNOCKOUT if target["id"] >= 4 else BUDGET_GROUPS
    cap = MAX_PER_COUNTRY.get(label, 3)

    squad = solve(ranked["rows"], budget, cap)
    base = {"label": label, "target": target, "captured_at": ranked["captured_at"],
            "budget": budget, "max_per_country": cap, "candidates": len(ranked["rows"]),
            "nations": len({r["nation"] for r in ranked["rows"]})}
    if not squad:
        return {**base, "squad": None}

    formation, xi, bench_gk, bench_out = report.select_xi(squad)
    fixtures = {p["id"]: pool.squad_fixture(target, p["squad_id"]) for p in xi}
    ranked_xi = sorted(xi, key=lambda p: -p["proj"])
    captain, vice = ranked_xi[0], ranked_xi[1]
    cost = round(sum(p["price"] for p in squad), 1)
    xi_proj = round(sum(p["proj"] for p in xi) + captain["proj"], 1)  # incluye doblete del capitán
    return {**base, "squad": squad, "formation": formation, "xi": xi, "bench_gk": bench_gk,
            "bench_out": bench_out, "fixtures": fixtures, "captain": captain, "vice": vice,
            "cost": cost, "bank": round(budget - cost, 1), "xi_proj": xi_proj}


def render_markdown(o: dict) -> str:
    f = "-".join(str(x) for x in o["formation"])
    L = [f"# Reset {o['label']} — squad óptimo (ILP)", ""]
    L.append(f"> `wcf optimize` · presupuesto **${o['budget']}M** · máx **{o['max_per_country']}/país** "
             f"· pool del {o['captured_at'][:10]}")
    L.append("> ⚠️ Óptimo sobre la **proyección v0** (precio + forma + matchup). Tan bueno como esos "
             "números; recalibrar pesos pesa más que el solver.")
    L.append("")
    L.append(f"## XI titular — {f} (proj {o['xi_proj']}, incluye capitán x2)")
    L.append("")
    L.append("| Pos | Jugador | Sel | $ | Proj | Own |")
    L.append("|---|---|---|---|---|---|")
    order = {"GK": 0, "DEF": 1, "MID": 2, "FWD": 3}
    for p in sorted(o["xi"], key=lambda x: (order[x["pos"]], -x["proj"])):
        tag = " (C)" if p["id"] == o["captain"]["id"] else (" (V)" if p["id"] == o["vice"]["id"] else "")
        L.append(f"| {p['pos']} | {p['name']}{tag} | {p['nation']} | {p['price']} | {p['proj']} | {p['ownership']}% |")
    L.append("")
    L.append(f"**Costo:** ${o['cost']}M · **banco:** ${o['bank']}M")
    L.append("")
    L.append("## Banca (orden de auto-subs)")
    if o["bench_gk"]:
        L.append(f"- GK: {o['bench_gk'][0]['name']} ({o['bench_gk'][0]['nation']})")
    for i, p in enumerate(o["bench_out"], 1):
        L.append(f"{i}. {p['name']} ({p['pos']} {p['nation']}, proj {p['proj']})")
    L.append("")
    return "\n".join(L)


def write_report(risk: strategy.RiskProfile, budget: float | None = None):
    o = optimize(risk, budget)
    if not o["squad"]:
        return None, o
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUTS_DIR / f"{o['label'].lower()}-reset.md"
    path.write_text(render_markdown(o), encoding="utf-8")
    return path, o
