"""Maintenance log NLP endpoints."""
from flask import Blueprint, request
from app.utils.response import ok, error
from app.services.nlp_service import analyze_note, analyze_log_file
from app.services.persistence import save_log_entry, get_log_entries
from app.utils.config import MAINTENANCE_LOG_PATH

bp = Blueprint("maint_logs", __name__)


@bp.get("/api/maintenance-logs")
def list_logs():
    severity   = request.args.get("severity")
    machine_id = request.args.get("machine_id")
    relevant   = request.args.get("relevant")
    limit      = min(int(request.args.get("limit", 100)), 500)
    offset     = int(request.args.get("offset", 0))

    rel_filter = None
    if relevant is not None:
        rel_filter = relevant.lower() == "true"

    entries = get_log_entries(severity=severity, relevant=rel_filter,
                               machine_id=machine_id, limit=limit, offset=offset)
    return ok({"entries": entries, "total": len(entries)})


@bp.post("/api/maintenance-logs")
def add_log():
    body = request.get_json(silent=True) or {}
    text = body.get("text", "").strip()
    if not text:
        return error("text field is required", 422)
    if len(text) > 2000:
        return error("Note too long (max 2000 characters)", 422)

    analysis = analyze_note(text)
    entry_id = save_log_entry(analysis)
    return ok({"entry_id": entry_id, **analysis}, "Note analyzed and saved", 201)


@bp.get("/api/maintenance-logs/analyze-file")
def analyze_file():
    results = analyze_log_file(MAINTENANCE_LOG_PATH)
    if not results:
        return ok({"entries": [], "message": "Maintenance log file not found or empty."})
    # Persist each result
    for r in results:
        save_log_entry(r)
    return ok({"entries": results, "count": len(results)})
