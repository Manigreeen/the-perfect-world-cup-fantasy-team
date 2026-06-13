"""Capa de acceso a datos sobre los snapshots de FIFA: carga el pool, las selecciones y las
rondas, y los une. Es la base que consumen el modelo y los reportes — nunca tocan HTTP directo.
"""

from datetime import datetime

from . import myteam, store


class NoSnapshotError(RuntimeError):
    pass


def _require(name: str):
    latest = store.load_latest(name)
    if not latest:
        raise NoSnapshotError(f"No hay snapshot '{name}' — corre `wcf pool` y `wcf rounds`")
    return latest


def load_players() -> tuple[str, list[dict]]:
    return _require("fifa_players")


def load_squads() -> dict[int, dict]:
    """squad_id → {name, group, abbr, isEliminated}."""
    return {s["id"]: s for s in _require("fifa_squads")[1]}


def load_rounds() -> list[dict]:
    return _require("fifa_rounds")[1]


def upcoming_round(rounds: list[dict]) -> dict:
    """La ronda objetivo de las transfers: la primera 'scheduled' (la que aún no arrancó)."""
    for r in sorted(rounds, key=lambda r: r["id"]):
        if r["status"] == "scheduled":
            return r
    return max(rounds, key=lambda r: r["id"])  # fallback: torneo terminado


def squad_fixture(round_: dict, squad_id: int) -> dict | None:
    """El partido de esa selección en la ronda, anotado desde su perspectiva (rival, local/visita)."""
    for t in round_.get("tournaments", []):
        if t["homeSquadId"] == squad_id:
            return {"opponent_id": t["awaySquadId"], "opponent": t["awaySquadName"],
                    "home": True, "date": t["date"], "venue": t.get("venueCity")}
        if t["awaySquadId"] == squad_id:
            return {"opponent_id": t["homeSquadId"], "opponent": t["homeSquadName"],
                    "home": False, "date": t["date"], "venue": t.get("venueCity")}
    return None


def my_team_matchups() -> dict:
    """Une mi squad (data/my-team.md) con los fixtures de la próxima ronda.

    Devuelve {round, captured_at, rows[...]} donde cada row tiene jugador, fixture y ownership.
    """
    captured_at, players = load_players()
    squads = load_squads()
    squad_names = {sid: s["name"] for sid, s in squads.items()}
    rounds = load_rounds()
    target = upcoming_round(rounds)

    rows = []
    for row in myteam.parse_my_team():
        p = myteam.find_player(row, players, squad_names)
        if p is None:
            rows.append({"name": row["name"], "role": row["role"], "found": False})
            continue
        fixture = squad_fixture(target, p["squadId"])
        rows.append({
            "name": p.get("knownName") or f"{p['firstName']} {p['lastName']}",
            "pos": p["position"],
            "role": row["role"],
            "country": squad_names.get(p["squadId"], "?"),
            "ownership": p["percentSelected"],
            "found": True,
            "fixture": fixture,
        })
    return {"round": target, "captured_at": captured_at, "rows": rows}


def fmt_kickoff(iso: str) -> str:
    """ISO con zona → 'Jue 18 17:00' legible."""
    dt = datetime.fromisoformat(iso)
    days = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    return f"{days[dt.weekday()]} {dt.day} {dt:%H:%M}"
