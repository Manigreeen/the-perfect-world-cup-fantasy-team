"""CLI del proyecto: `wcf <comando>`. Cada comando descarga, snapshotea y resume en una línea."""

import argparse
import sys

from . import historical, myteam, pool, projection, recommender, store, strategy
from .config import FREE_TRANSFERS, ROUND_LABELS
from .sources import api_football, fifa_fantasy
from .sources import news as news_src


def cmd_status(_args) -> None:
    body = api_football.status()
    acct = body.get("response", {})
    sub = acct.get("subscription", {})
    req = acct.get("requests", {})
    print(f"Plan: {sub.get('plan')} · requests hoy: {req.get('current')}/{req.get('limit_day')}")


def cmd_fixtures(_args) -> None:
    body = api_football.fixtures()
    path = store.save_snapshot("fixtures", body["response"])
    print(f"{body['results']} fixtures → {path}")


def cmd_injuries(_args) -> None:
    body = api_football.injuries()
    path = store.save_snapshot("injuries", body["response"])
    print(f"{body['results']} registros de lesión/sanción → {path}")


def cmd_players(args) -> None:
    page, total, all_players = 1, 1, []
    while page <= total:
        body = api_football.players(page=page)
        all_players.extend(body["response"])
        total = body["paging"]["total"]
        page += 1
        if args.max_pages and page > args.max_pages:
            break
    path = store.save_snapshot("players", all_players)
    print(f"{len(all_players)} jugadores ({page - 1} páginas) → {path}")


def cmd_pool(_args) -> None:
    players = fifa_fantasy.fetch_players()
    squads = fifa_fantasy.fetch_squads()
    p_path = store.save_snapshot("fifa_players", players)
    store.save_snapshot("fifa_squads", squads)
    low_own = sum(1 for p in players if p["percentSelected"] < 5)
    print(f"{len(players)} jugadores ({low_own} con ownership <5%) → {p_path}")


def cmd_rounds(_args) -> None:
    rounds = fifa_fantasy.fetch_rounds()
    path = store.save_snapshot("fifa_rounds", rounds)
    for r in rounds:
        print(f"ronda {r['id']}: {r['status']:>10}  lockout {r['startDate']}")
    print(f"→ {path}")


def cmd_myteam(_args) -> None:
    try:
        print("\n".join(myteam.validate()))
    except FileNotFoundError as exc:
        sys.exit(f"error: {exc}")


def cmd_matchups(_args) -> None:
    try:
        data = pool.my_team_matchups()
    except pool.NoSnapshotError as exc:
        sys.exit(f"error: {exc}")
    r = data["round"]
    label = ROUND_LABELS.get(r["id"], f"Ronda {r['id']}")
    print(f"Matchups de {label} · lockout {pool.fmt_kickoff(r['startDate'])} · "
          f"pool del {data['captured_at'][:10]}\n")

    def sort_key(row):  # titulares primero, luego por horario (insight de capitanía)
        fx = row.get("fixture")
        return (0 if row["role"].lower().startswith("titular") else 1,
                fx["date"] if fx else "9999")

    for row in sorted(data["rows"], key=sort_key):
        if not row["found"]:
            print(f"  ✗ {row['name']}: no encontrado en el pool")
            continue
        fx = row["fixture"]
        if not fx:
            print(f"  {row['name']}: sin partido en {label} (¿eliminado?)")
            continue
        loc = "vs" if fx["home"] else " @"
        scout = " ⭐<5%" if row["ownership"] < 5 else ""
        print(f"  {row['role'][:3]:<3} {row['name']:<19} {row['pos']:>3}  "
              f"{loc} {fx['opponent']:<15} {pool.fmt_kickoff(fx['date'])}  "
              f"own {row['ownership']}%{scout}")


def cmd_history(args) -> None:
    """Baja priors históricos (WC2022) de las selecciones vivas, acotado y resumible."""
    try:
        summary = historical.run_fetch(max_requests=args.max_requests)
    except api_football.ApiFootballError as exc:
        sys.exit(f"error: {exc}")
    print(f"Bajadas {len(summary['fetched'])} selecciones · ya cacheadas {summary['skipped_cached']} "
          f"· requests usados {summary['requests_used']}")
    if summary["fetched"]:
        print("  nuevas: " + ", ".join(summary["fetched"]))
    if summary["missing_from_2022"]:
        print(f"  sin histórico WC2022 ({len(summary['missing_from_2022'])}, usan prior por defecto): "
              + ", ".join(summary["missing_from_2022"]))
    if summary["stopped_early"]:
        print("  ⚠ corte por tope de quota — corre `wcf history` de nuevo mañana para continuar")

    # Feedback: cobertura de priors sobre mi propio squad
    index = historical.build_priors()
    if not index:
        return
    print("\nPriors de mi squad (tasas por-90 del WC2022):")
    squad_names = {sid: s["name"] for sid, s in pool.load_squads().items()}
    _, players = pool.load_players()
    for row in myteam.parse_my_team():
        p = myteam.find_player(row, players, squad_names)
        if not p:
            continue
        nation = squad_names.get(p["squadId"], "")
        pr = historical.prior_for(p["firstName"], p["lastName"], nation, index)
        name = p.get("knownName") or f"{p['firstName']} {p['lastName']}"
        if pr:
            print(f"  {name:<20} tiros/90={pr['shots90']:<5} keyp/90={pr['key_passes90']:<5} "
                  f"tackles/90={pr['tackles90']:<5} GI/90={pr['goal_involvement90']:<5} ({pr['minutes']}min)")
        else:
            print(f"  {name:<20} — sin histórico WC2022 (prior por defecto)")


def cmd_news(args) -> None:
    """Titulares relevantes para mi squad desde RSS gratis (P1: lesiones/rotación de último momento)."""
    items = news_src.fetch_all()
    if not items:
        sys.exit("error: ninguna fuente RSS respondió")
    store.save_snapshot("news", items)

    # Dos clases de entidad: nombres de jugadores (señal alta) y naciones (contexto, más ruidoso —
    # 'Spain' matchea F1/dardos). Se filtra con ambas pero se reportan por separado.
    player_ents: set[str] = set()
    nation_ents: set[str] = set()
    squad_names = {sid: s["name"] for sid, s in pool.load_squads().items()}
    _, players = pool.load_players()
    for row in myteam.parse_my_team():
        p = myteam.find_player(row, players, squad_names)
        if not p:
            continue
        player_ents.add(p.get("knownName") or p["lastName"])
        nation_ents.add(squad_names.get(p["squadId"], ""))

    hits = news_src.filter_by_entities(items, sorted(player_ents | nation_ents))
    direct = [h for h in hits if any(m in player_ents for m in h["matched"])]
    context = [h for h in hits if h not in direct]
    print(f"{len(items)} titulares de {len(news_src.FEEDS)} fuentes · "
          f"{len(direct)} mencionan a tus jugadores, {len(context)} contexto de selección\n")

    def show(title, rows):
        if not rows:
            return
        print(title)
        for it in rows[: args.limit]:
            when = it["published"][:16] if it["published"] else ""
            print(f"  [{it['source']}] {it['title']}")
            print(f"    ⮑ {', '.join(it['matched'])} · {when}")
        print()

    show("🎯 Menciones directas de tus jugadores", direct)
    show("🌍 Contexto de tus selecciones (ruido posible)", context)


def _my_squad_ids() -> set[int]:
    squad_names = {sid: s["name"] for sid, s in pool.load_squads().items()}
    _, players = pool.load_players()
    ids = set()
    for row in myteam.parse_my_team():
        p = myteam.find_player(row, players, squad_names)
        if p:
            ids.add(p["id"])
    return ids


def cmd_rank(args) -> None:
    """Ranking de profitability para la próxima ronda: proyección, valor, scouting."""
    try:
        risk = strategy.active_profile(args.risk)
        data = projection.rank_pool(risk)
    except (pool.NoSnapshotError, ValueError) as exc:
        sys.exit(f"error: {exc}")

    rows = data["rows"]
    if args.pos:
        rows = [r for r in rows if r["pos"] == args.pos.upper()]
    rows.sort(key=lambda r: r[args.by], reverse=True)
    mine = _my_squad_ids()
    label = ROUND_LABELS.get(data["round"]["id"], f"R{data['round']['id']}")

    print(f"Ranking {label} · orden por {args.by} · riesgo {risk.name} · pool {data['captured_at'][:10]}")
    print(f"(proj = pts esperados; val = proj/precio; ★ = tu squad; ⭐ = scouting <5%)\n")
    print(f"  {'#':>2}  {'jugador':<20} {'pos':>3} {'sel':<14} {'$':>5} {'proj':>5} {'val':>5}  own")
    for i, r in enumerate(rows[: args.limit], 1):
        star = "★" if r["id"] in mine else " "
        scout = "⭐" if r["ownership"] < 5 else " "
        print(f"{star}{scout}{i:>2}  {r['name']:<20.20} {r['pos']:>3} {r['nation']:<14.14} "
              f"{r['price']:>5} {r['proj']:>5} {r['value']:>5}  {r['ownership']}%")


def cmd_transfers(args) -> None:
    """Recomienda las transfers de la próxima ronda (o plantarse) según el dial de riesgo."""
    try:
        risk = strategy.active_profile(args.risk)
        label = ROUND_LABELS.get(pool.upcoming_round(pool.load_rounds())["id"], "?")
        free = args.free if args.free is not None else (FREE_TRANSFERS.get(label) or 2)
        rec = recommender.recommend(risk, free_transfers=free, phase=label)
    except (pool.NoSnapshotError, ValueError) as exc:
        sys.exit(f"error: {exc}")

    print(f"Transfers {label} · {free} libres · riesgo {risk.name} (umbral +{rec['threshold']} pts) "
          f"· banco ${rec['bank']}M · pool {rec['captured_at'][:10]}\n")
    if not rec["swaps"]:
        print("  ✋ Plantarse: ningún cambio supera el umbral. Guardar las transfers")
        print("     (en grupos, 1 transfer sin usar hace rollover a la siguiente ronda).")
        return
    for i, s in enumerate(rec["swaps"], 1):
        o, n = s["out"], s["in"]
        print(f"  {i}. OUT {o['name']} ({o['pos']} {o['nation']}, ${o['price']}, proj {o['proj']})")
        print(f"     IN  {n['name']} ({n['pos']} {n['nation']}, ${n['price']}, proj {n['proj']})")
        print(f"     +{s['gain']} pts · {s['why']}\n")
    print(f"  Ganancia proyectada total: +{rec['total_gain']} pts · banco resultante ${rec['bank']}M")


def main() -> None:
    parser = argparse.ArgumentParser(prog="wcf", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Plan y cuota usada de API-Football (no consume requests)")
    sub.add_parser("fixtures", help="Descarga el calendario del Mundial y lo snapshotea")
    sub.add_parser("injuries", help="Descarga lesionados/sancionados y los snapshotea")
    p_players = sub.add_parser("players", help="Descarga stats por jugador (paginado)")
    p_players.add_argument("--max-pages", type=int, default=0, help="límite de páginas (0 = todas)")
    sub.add_parser("pool", help="Snapshot del pool fantasy de FIFA (precios, ownership) — sin auth")
    sub.add_parser("rounds", help="Rondas con lockouts reales y fixtures, desde play.fifa.com")
    sub.add_parser("myteam", help="Valida data/my-team.md contra el último snapshot del pool")
    sub.add_parser("matchups", help="Fixtures de la próxima ronda para tu squad (rival, horario, ownership)")
    p_hist = sub.add_parser("history", help="Baja priors históricos (WC2022) de selecciones vivas — acotado, resumible")
    p_hist.add_argument("--max-requests", type=int, default=80, help="tope de requests por corrida (quota free: 100/día)")
    p_news = sub.add_parser("news", help="Titulares RSS gratis (BBC/Guardian/Sky) filtrados a tu squad")
    p_news.add_argument("--limit", type=int, default=15, help="máximo de titulares a mostrar")
    p_rank = sub.add_parser("rank", help="Ranking de profitability (proyección v0) para la próxima ronda")
    p_rank.add_argument("--by", choices=["proj", "value"], default="value", help="ordenar por pts esperados o valor")
    p_rank.add_argument("--pos", choices=["GK", "DEF", "MID", "FWD"], help="filtrar por posición")
    p_rank.add_argument("--limit", type=int, default=25, help="cuántos mostrar")
    p_rank.add_argument("--risk", choices=["conservative", "moderate", "aggressive"], help="override del dial de riesgo")
    p_tr = sub.add_parser("transfers", help="Recomienda las transfers de la próxima ronda (o plantarse)")
    p_tr.add_argument("--risk", choices=["conservative", "moderate", "aggressive"], help="override del dial de riesgo")
    p_tr.add_argument("--free", type=int, help="transfers libres disponibles (default: las de la ronda)")

    args = parser.parse_args()
    handler = {
        "status": cmd_status,
        "fixtures": cmd_fixtures,
        "injuries": cmd_injuries,
        "players": cmd_players,
        "pool": cmd_pool,
        "rounds": cmd_rounds,
        "myteam": cmd_myteam,
        "matchups": cmd_matchups,
        "history": cmd_history,
        "news": cmd_news,
        "rank": cmd_rank,
        "transfers": cmd_transfers,
    }[args.command]
    try:
        handler(args)
    except api_football.ApiFootballError as exc:
        sys.exit(f"error: {exc}")


if __name__ == "__main__":
    main()
