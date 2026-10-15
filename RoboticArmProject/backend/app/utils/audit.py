"""
Structured audit/event logger.
Writes JSON-lines to audit_log.jsonl — no secrets, no PII.
"""
import json
import logging
import os
from datetime import datetime, timezone
from app.utils.config import AUDIT_LOG_PATH

logger = logging.getLogger(__name__)

_ensure_done = False

def _ensure_dir():
    global _ensure_done
    if not _ensure_done:
        os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
        _ensure_done = True


def log_event(
    event_type: str,
    machine_id: str = None,
    severity: str = "info",
    source: str = "system",
    description: str = "",
    decision: str = None,
    evidence: dict = None,
):
    _ensure_dir()
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "machine_id": machine_id,
        "severity": severity,
        "source": source,
        "description": description,
        "decision": decision,
        "evidence": evidence or {},
    }
    try:
        with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception as exc:
        logger.warning("Audit log write failed: %s", exc)
    return record


def read_events(limit: int = 500, offset: int = 0) -> list:
    _ensure_dir()
    if not os.path.exists(AUDIT_LOG_PATH):
        return []
    events = []
    try:
        with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    except Exception as exc:
        logger.warning("Audit log read failed: %s", exc)
    # newest first
    events.reverse()
    return events[offset: offset + limit]


def event_count() -> int:
    if not os.path.exists(AUDIT_LOG_PATH):
        return 0
    count = 0
    try:
        with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
    except Exception:
        pass
    return count
