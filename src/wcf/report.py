"""Reporte de ronda: junta transfers + XI + capitán + banca en un markdown auditable
(`outputs/<ronda>-reporte.md`). Es el deliverable de cada deadline (principio 2 de docs/04:
guardar lo que el modelo recomendó para poder auditarlo después).
"""

from datetime import datetime

from . import pool, recommender, strategy
from .config import DEADLINES, OUTPUTS_DIR, ROUND_LABELS, VALID_FORMATIONS


def select_xi(squad: list[dict]):
    """Elige formación válida y XI que maximizan la proyección total. Devuelve (formación, xi, banca)."""
    by = {pos: sorted([p for p in squad if p["pos"] == pos], key=lambda x: -x["proj"])
          for pos in ("GK", "DEF", "MID", "FWD")}
    best = None
    for d, m, f in VALID_FORMATIONS:
        if not by["GK"] or len(by["DEF"]) < d or len(by["MID"]) < m or len(by["FWD"]) < f:
            continue
        xi = [by["GK"][0]] + by["DEF"][:d] + by["MID"][:m] + by["FWD"][:f]
        total = sum(p["proj"] for p in xi)
        if best is None or total > best[0]:
            best = (total, (d, m, f), xi)
    _, formation, xi = best
    xi_ids = {p["id"] for p in xi}
    bench = [p for p in squad if p["id"] not in xi_ids]
    bench_gk = [p for p in bench if p["pos"] == "GK"]
    bench_out = sorted([p for p in bench if p["pos"] != "GK"], key=lambda x: -x["proj"])
    return formation, xi, bench_gk, bench_out


def build(risk: strategy.RiskProfile, free_transfers: int | None = None) -> dict:
    rounds = pool.load_rounds()
    target = pool.upcoming_round(rounds)
    label = ROUND_LABELS.get(target["id"], f"R{target['id']}")
    from .config import FREE_TRANSFERS
    free = free_transfers if free_transfers is not None else (FREE_TRANSFERS.get(label) or 2)

    rec = recommender.recommend(risk, free_transfers=free, phase=label)
    formation, xi, bench_gk, bench_out = select_xi(rec["squad"])

    # Capitán/vice = top-2 proyección del XI. Timing (P6): kickoff de cada uno para el switch.
    fixtures = {p["id"]: pool.squad_fixture(target, p["squad_id"]) for p in xi}
    ranked_xi = sorted(xi, key=lambda p: -p["proj"])
    captain, vice = ranked_xi[0], ranked_xi[1]
    return {"label": label, "target": target, "risk": risk, "rec": rec, "formation": formation,
            "xi": xi, "bench_gk": bench_gk, "bench_out": bench_out, "fixtures": fixtures,
            "captain": captain, "vice": vice}


def _ko(fixture) -> str:
    return pool.fmt_kickoff(fixture["date"]) if fixture else "?"


def render_markdown(r: dict) -> str:
    label, target, rec = r["label"], r["target"], r["rec"]
    deadline = DEADLINES.get(label, target["startDate"])
    f = "-".join(str(x) for x in r["formation"])
    L = []
    L.append(f"# Reporte {label} — {datetime.now():%Y-%m-%d %H:%M}")
    L.append("")
    L.append(f"> `wcf report` · riesgo **{r['risk'].name}** · lockout **{deadline}** · "
             f"pool del {rec['captured_at'][:10]}")
    L.append("> ⚠️ Proyección v0: se apoya en el prior de precio + MD1 parcial. "
             "Recalibrar cuando MD1 cierre (18 jun).")
    L.append("")

    L.append(f"## Transfers ({rec['free_transfers']} libres · umbral +{rec['threshold']} pts · "
             f"banco ${rec['bank']}M)")
    if not rec["swaps"]:
        L.append("- ✋ **Plantarse** — ningún cambio supera el umbral. Guardar la transfer "
                 "(rollover de 1 a la siguiente ronda de grupos).")
    else:
        for i, s in enumerate(rec["swaps"], 1):
            o, n = s["out"], s["in"]
            L.append(f"{i}. **OUT** {o['name']} ({o['pos']} {o['nation']}, ${o['price']}, proj {o['proj']}) "
                     f"→ **IN** {n['name']} ({n['pos']} {n['nation']}, ${n['price']}, proj {n['proj']}) "
                     f"· **+{s['gain']}** · _{s['why']}_")
        L.append(f"\n**Ganancia proyectada:** +{rec['total_gain']} pts")
    L.append("")

    xi_total = round(sum(p["proj"] for p in r["xi"]), 1)
    L.append(f"## XI titular — {f} (proyección {xi_total})")
    L.append("")
    L.append("| Pos | Jugador | Sel | $ | Proj | Own |")
    L.append("|---|---|---|---|---|---|")
    order = {"GK": 0, "DEF": 1, "MID": 2, "FWD": 3}
    for p in sorted(r["xi"], key=lambda x: (order[x["pos"]], -x["proj"])):
        cap = " (C)" if p["id"] == r["captain"]["id"] else (" (V)" if p["id"] == r["vice"]["id"] else "")
        L.append(f"| {p['pos']} | {p['name']}{cap} | {p['nation']} | {p['price']} | {p['proj']} | {p['ownership']}% |")
    L.append("")

    cap, vice = r["captain"], r["vice"]
    L.append("## Capitán y vice")
    L.append(f"- **Capitán:** {cap['name']} (proj {cap['proj']}) — kickoff {_ko(r['fixtures'][cap['id']])}")
    L.append(f"- **Vice:** {vice['name']} (proj {vice['proj']}) — kickoff {_ko(r['fixtures'][vice['id']])}")
    early = min(r["xi"], key=lambda p: (r["fixtures"][p["id"]] or {}).get("date", "9999"))
    L.append(f"- **Timing (P6):** el más temprano del XI es {early['name']} ({_ko(r['fixtures'][early['id']])}); "
             "capitanear inicialmente a alguien que juega temprano deja abierta la ventana de switch "
             "a un jugador posterior. Recordar: el primer cambio manual anula auto-subs y el doblete del vice.")
    L.append("")

    L.append("## Banca (orden de auto-subs)")
    if r["bench_gk"]:
        L.append(f"- GK: {r['bench_gk'][0]['name']} ({r['bench_gk'][0]['nation']})")
    for i, p in enumerate(r["bench_out"], 1):
        L.append(f"{i}. {p['name']} ({p['pos']} {p['nation']}, proj {p['proj']})")
    L.append("")
    return "\n".join(L)


def write_report(risk: strategy.RiskProfile, free_transfers: int | None = None):
    r = build(risk, free_transfers)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUTS_DIR / f"{r['label'].lower()}-reporte.md"
    path.write_text(render_markdown(r), encoding="utf-8")
    return path, r
