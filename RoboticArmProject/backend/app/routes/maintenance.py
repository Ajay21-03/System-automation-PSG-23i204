"""Maintenance cases CRUD endpoints."""
from flask import Blueprint, request
from app.utils.response import ok, error
from app.services.persistence import (
    create_maintenance_case, get_maintenance_cases,
    update_maintenance_case, maintenance_case_count
)
from app.utils.audit import log_event

bp = Blueprint("maintenance", __name__)

VALID_STATUSES = {"open", "acknowledged", "scheduled", "resolved"}


@bp.get("/api/maintenance")
def list_cases():
    status     = request.args.get("status")
    machine_id = request.args.get("machine_id")
    limit      = min(int(request.args.get("limit", 50)), 200)
    offset     = int(request.args.get("offset", 0))
    cases = get_maintenance_cases(status=status, machine_id=machine_id,
                                   limit=limit, offset=offset)
    return ok({"cases": cases, "total": len(cases)})


@bp.post("/api/maintenance")
def create_case():
    body = request.get_json(silent=True) or {}
    machine_id  = body.get("machine_id")
    decision    = body.get("decision")
    description = body.get("description", "")
    severity    = body.get("severity", "warning")
    joint       = body.get("joint")
    evidence    = body.get("evidence", [])
    priority    = body.get("priority", "medium")

    if not machine_id or not decision:
        return error("machine_id and decision are required", 422)

    result = create_maintenance_case(
        machine_id=machine_id, decision=decision,
        description=description, severity=severity,
        joint=joint, evidence=evidence, priority=priority
    )

    if result.get("duplicate"):
        return ok({"duplicate": True, "id": result["id"],
                   "message": "Open case already exists for this machine and decision."})

    log_event("maintenance_case_created", machine_id=machine_id,
              severity=severity, decision=decision,
              description=description, evidence={"case_id": result["id"]})
    return ok(result, "Maintenance case created", 201)


@bp.patch("/api/maintenance/<int:case_id>")
def update_case(case_id):
    body   = request.get_json(silent=True) or {}
    status = body.get("status")
    desc   = body.get("description")

    if status and status not in VALID_STATUSES:
        return error(f"Invalid status. Allowed: {sorted(VALID_STATUSES)}", 422)

    result = update_maintenance_case(case_id, status=status, description=desc)
    if "error" in result:
        return error(result["error"], 404)

    log_event("maintenance_case_updated", machine_id=result.get("machine_id"),
              description=f"Case {case_id} → {status or 'updated'}")
    return ok(result)
