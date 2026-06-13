"""Snapshots versionables en data/: todo dato que alimenta una recomendación queda en disco
(principio 4 del plan: reproducibilidad del backtest)."""

import json
from datetime import datetime, timezone
from pathlib import Path

from .config import SNAPSHOTS_DIR


def save_snapshot(name: str, payload) -> Path:
    """Guarda payload en data/snapshots/<YYYY-MM-DD>/<name>.json con timestamp de captura."""
    now = datetime.now(timezone.utc)
    path = SNAPSHOTS_DIR / now.strftime("%Y-%m-%d") / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {"captured_at": now.isoformat(timespec="seconds"), "data": payload}
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_latest(name: str):
    """Devuelve (captured_at, data) del snapshot más reciente con ese nombre, o None."""
    if not SNAPSHOTS_DIR.exists():
        return None
    for day_dir in sorted(SNAPSHOTS_DIR.iterdir(), reverse=True):
        path = day_dir / f"{name}.json"
        if path.is_file():
            doc = json.loads(path.read_text(encoding="utf-8"))
            return doc["captured_at"], doc["data"]
    return None
