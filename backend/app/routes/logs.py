"""Event / audit log endpoints with CSV export."""
import csv
import io
from flask import Blueprint, request, Response
from app.utils.response import ok
from app.utils.audit import read_events, event_count

bp = Blueprint("logs", __name__)


@bp.get("/api/logs")
def logs():
    limit  = min(int(request.args.get("limit",  100)), 500)
    offset = int(request.args.get("offset", 0))
    events = read_events(limit=limit, offset=offset)
    total  = event_count()
    return ok({"events": events, "total": total, "limit": limit, "offset": offset})


@bp.get("/api/logs/export")
def export_csv():
    events = read_events(limit=10000)
    if not events:
        return Response("No events.", mimetype="text/plain")

    si  = io.StringIO()
    writer = csv.DictWriter(si, fieldnames=list(events[0].keys()))
    writer.writeheader()
    writer.writerows(events)
    output = si.getvalue()

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=audit_log.csv"},
    )
