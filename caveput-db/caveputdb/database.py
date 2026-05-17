import sqlite3
import json
from datetime import datetime, timezone
from . import config

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS catalog (
    id      INTEGER PRIMARY KEY CHECK (id = 1),
    ingredients_json    TEXT,
    template_groups_json TEXT,
    synced_at           TEXT
);
INSERT OR IGNORE INTO catalog (id) VALUES (1);

CREATE TABLE IF NOT EXISTS sync_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    synced_at       TEXT NOT NULL,
    status          TEXT NOT NULL,
    ingredient_count INTEGER,
    error_message   TEXT
);
"""

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.executescript(_CREATE_SQL)

def save_catalog(ingredients: list, template_groups: list):
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        conn.execute(
            "UPDATE catalog SET ingredients_json=?, template_groups_json=?, synced_at=? WHERE id=1",
            (json.dumps(ingredients), json.dumps(template_groups), now)
        )
        conn.execute(
            "INSERT INTO sync_log (synced_at, status, ingredient_count) VALUES (?,?,?)",
            (now, "ok", len(ingredients))
        )

def log_sync_error(error: str):
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO sync_log (synced_at, status, error_message) VALUES (?,?,?)",
            (now, "error", error)
        )

def get_catalog() -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM catalog WHERE id=1").fetchone()
    if not row or not row["ingredients_json"]:
        return None
    return {
        "ingredients": json.loads(row["ingredients_json"] or "[]"),
        "template_groups": json.loads(row["template_groups_json"] or "[]"),
        "synced_at": row["synced_at"],
    }

def get_sync_status() -> dict:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM sync_log ORDER BY id DESC LIMIT 1"
        ).fetchone()
        catalog = conn.execute("SELECT synced_at FROM catalog WHERE id=1").fetchone()
    if not row:
        return {"status": "never_synced", "last_sync": None, "ingredient_count": 0}
    return {
        "status": row["status"],
        "last_sync": row["synced_at"],
        "ingredient_count": row["ingredient_count"] or 0,
        "error": row["error_message"],
    }
