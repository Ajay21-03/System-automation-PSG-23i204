"""
SQLite persistence for maintenance cases, security events,
maintenance log entries, and dataset/model metadata.
"""
import sqlite3
import json
import logging
import os
from datetime import datetime, timezone
from contextlib import contextmanager
from app.utils.config import DB_PATH, DATA_DIR

logger = logging.getLogger(__name__)


def _ensure_db_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


@contextmanager
def _conn():
    _ensure_db_dir()
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def init_db():
    """Create tables if they don't exist."""
    with _conn() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS maintenance_cases (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id  TEXT NOT NULL,
            joint       TEXT,
            decision    TEXT NOT NULL,
            severity    TEXT NOT NULL DEFAULT 'warning',
            status      TEXT NOT NULL DEFAULT 'open',
            description TEXT,
            evidence    TEXT,
            priority    TEXT DEFAULT 'medium',
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS maintenance_log_entries (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id  TEXT,
            joint       TEXT,
            text        TEXT NOT NULL,
            severity    TEXT,
            relevant    INTEGER,
            detected_terms TEXT,
            explanation TEXT,
            analyzed_at TEXT NOT NULL,
            created_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS security_events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id  TEXT,
            sensor      TEXT,
            severity    TEXT,
            reason      TEXT,
            value       TEXT,
            detected_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS model_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            trained_at  TEXT NOT NULL,
            accuracy    REAL,
            macro_f1    REAL,
            dataset_size INTEGER,
            metrics_json TEXT
        );
        """)
    logger.info("Database initialised at %s", DB_PATH)


# --------------- Maintenance Cases ----------------------------------------

def create_maintenance_case(
    machine_id: str, decision: str, description: str = "",
    severity: str = "warning", joint: str = None,
    evidence: list = None, priority: str = "medium"
) -> dict:
    """
    Create a maintenance case only if no open/acknowledged case already
    exists for this machine+decision combination (prevents duplicates on refresh).
    """
    now = datetime.now(timezone.utc).isoformat()
    with _conn() as con:
        # De-duplicate check
        existing = con.execute(
            "SELECT id FROM maintenance_cases WHERE machine_id=? AND decision=? AND status IN ('open','acknowledged')",
            (machine_id, decision)
        ).fetchone()
        if existing:
            return {"duplicate": True, "id": existing["id"]}

        evidence_json = json.dumps(evidence or [])
        cur = con.execute(
            """INSERT INTO maintenance_cases
               (machine_id, joint, decision, severity, status, description, evidence, priority, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (machine_id, joint, decision, severity, "open",
             description, evidence_json, priority, now, now)
        )
        return {"id": cur.lastrowid, "duplicate": False}


def get_maintenance_cases(status: str = None, machine_id: str = None,
                           limit: int = 100, offset: int = 0) -> list:
    with _conn() as con:
        base = "SELECT * FROM maintenance_cases WHERE 1=1"
        params = []
        if status:
            base += " AND status=?"
            params.append(status)
        if machine_id:
            base += " AND machine_id=?"
            params.append(machine_id)
        base += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params += [limit, offset]
        rows = con.execute(base, params).fetchall()
    return [dict(r) for r in rows]


def update_maintenance_case(case_id: int, status: str = None,
                             description: str = None) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    with _conn() as con:
        row = con.execute("SELECT * FROM maintenance_cases WHERE id=?", (case_id,)).fetchone()
        if not row:
            return {"error": "Not found"}
        updates = []
        params  = []
        if status:
            updates.append("status=?")
            params.append(status)
        if description:
            updates.append("description=?")
            params.append(description)
        updates.append("updated_at=?")
        params.append(now)
        params.append(case_id)
        con.execute(f"UPDATE maintenance_cases SET {', '.join(updates)} WHERE id=?", params)
        updated = con.execute("SELECT * FROM maintenance_cases WHERE id=?", (case_id,)).fetchone()
    return dict(updated)


def maintenance_case_count() -> int:
    with _conn() as con:
        row = con.execute("SELECT COUNT(*) as c FROM maintenance_cases").fetchone()
    return row["c"]


# --------------- Maintenance Log Entries ------------------------------------

def save_log_entry(entry: dict) -> int:
    now = datetime.now(timezone.utc).isoformat()
    with _conn() as con:
        cur = con.execute(
            """INSERT INTO maintenance_log_entries
               (machine_id, joint, text, severity, relevant, detected_terms,
                explanation, analyzed_at, created_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                entry.get("arm_id"), entry.get("joint"), entry.get("original_text",""),
                entry.get("severity","info"), int(entry.get("relevant", False)),
                json.dumps(entry.get("detected_terms",[])),
                entry.get("explanation",""), entry.get("analyzed_at", now), now
            )
        )
    return cur.lastrowid


def get_log_entries(severity: str = None, relevant: bool = None,
                    machine_id: str = None, limit: int = 100, offset: int = 0) -> list:
    with _conn() as con:
        base = "SELECT * FROM maintenance_log_entries WHERE 1=1"
        params = []
        if severity:
            base += " AND severity=?"
            params.append(severity)
        if relevant is not None:
            base += " AND relevant=?"
            params.append(int(relevant))
        if machine_id:
            base += " AND machine_id=?"
            params.append(machine_id)
        base += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params += [limit, offset]
        rows = con.execute(base, params).fetchall()
    return [dict(r) for r in rows]


# --------------- Security Events -------------------------------------------

def save_security_event(machine_id: str, sensor: str, severity: str,
                         reason: str, value=None) -> int:
    now = datetime.now(timezone.utc).isoformat()
    with _conn() as con:
        cur = con.execute(
            """INSERT INTO security_events (machine_id, sensor, severity, reason, value, detected_at)
               VALUES (?,?,?,?,?,?)""",
            (machine_id, sensor, severity, reason, str(value), now)
        )
    return cur.lastrowid


def get_security_events(limit: int = 200, offset: int = 0) -> list:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM security_events ORDER BY detected_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()
    return [dict(r) for r in rows]


# --------------- Model History ---------------------------------------------

def record_training(metrics: dict):
    now = datetime.now(timezone.utc).isoformat()
    with _conn() as con:
        con.execute(
            """INSERT INTO model_history (trained_at, accuracy, macro_f1, dataset_size, metrics_json)
               VALUES (?,?,?,?,?)""",
            (
                metrics.get("trained_at", now),
                metrics.get("accuracy"),
                metrics.get("macro_f1"),
                metrics.get("dataset_size"),
                json.dumps(metrics),
            )
        )


def get_training_history(limit: int = 20) -> list:
    with _conn() as con:
        rows = con.execute(
            "SELECT id, trained_at, accuracy, macro_f1, dataset_size FROM model_history ORDER BY trained_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]
