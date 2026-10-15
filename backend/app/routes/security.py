"""Sensor integrity / security events endpoints."""
from flask import Blueprint, request
from app.utils.response import ok, error
from app.services.integrity_service import (
    full_integrity_check, simulate_torque_spoofing
)
from app.services.persistence import save_security_event, get_security_events
from app.services import dataset_generator as dg
from app.utils.audit import log_event

bp = Blueprint("security", __name__)


@bp.get("/api/security/events")
def events():
    limit  = min(int(request.args.get("limit", 200)), 500)
    offset = int(request.args.get("offset", 0))
    evts   = get_security_events(limit=limit, offset=offset)
    return ok({"events": evts, "total": len(evts)})


@bp.post("/api/security/simulate")
def simulate():
    body  = request.get_json(silent=True) or {}
    arm_id= body.get("arm_id", "ARM-001")
    joint = body.get("joint", "shoulder")
    result= simulate_torque_spoofing(arm_id=arm_id, joint=joint)

    # Persist security events from spoofed check
    for evt in result["spoofed_integrity"]["events"]:
        save_security_event(arm_id, evt.get("sensor",""), evt["severity"], evt["reason"], evt.get("value"))

    log_event("security_simulation", machine_id=arm_id, severity="warning",
              description="Torque-spoofing simulation executed (demo data only)",
              source="security_module")
    return ok(result)


@bp.post("/api/security/check")
def check():
    body = request.get_json(silent=True) or {}
    reading    = body.get("reading", {})
    previous   = body.get("previous", {})
    machine_id = body.get("machine_id", "UNKNOWN")

    if not reading:
        return error("reading object is required", 422)

    result = full_integrity_check(reading, previous=previous, machine_id=machine_id)

    for evt in result["events"]:
        save_security_event(machine_id, evt.get("sensor",""),
                            evt["severity"], evt["reason"], evt.get("value"))

    return ok(result)


@bp.get("/api/security/scan-dataset")
def scan_dataset():
    """Run integrity checks across the loaded dataset and return summary."""
    try:
        df = dg.load_dataset()
    except FileNotFoundError:
        return ok({"available": False, "events": []})

    events_found = []
    prev = None
    for _, row in df.iterrows():
        reading = row.to_dict()
        result  = full_integrity_check(reading, previous=prev,
                                        machine_id=str(row.get("arm_id","?")))
        if result["events"]:
            for evt in result["events"]:
                evt["arm_id"]    = row.get("arm_id")
                evt["timestamp"] = str(row.get("timestamp",""))
                events_found.append(evt)
                save_security_event(
                    str(row.get("arm_id","")),
                    evt.get("sensor",""),
                    evt["severity"],
                    evt["reason"],
                    evt.get("value")
                )
        prev = reading

    return ok({
        "available":   True,
        "total_events":len(events_found),
        "events":      events_found[:200],
        "note":        "Scanned entire dataset. Only first 200 events shown.",
    })
