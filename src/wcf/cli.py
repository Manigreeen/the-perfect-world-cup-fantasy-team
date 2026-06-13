"""CLI del proyecto: `wcf <comando>`. Cada comando descarga, snapshotea y resume en una línea."""

import argparse
import sys

from . import myteam, pool, store
from .config import ROUND_LABELS
from .sources import api_football, fifa_fantasy


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
    }[args.command]
    try:
        handler(args)
    except api_football.ApiFootballError as exc:
        sys.exit(f"error: {exc}")


if __name__ == "__main__":
    main()
