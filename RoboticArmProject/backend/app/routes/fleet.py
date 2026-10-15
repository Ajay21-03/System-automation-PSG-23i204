"""Fleet and machine detail endpoints."""
import logging
from flask import Blueprint, request
from app.utils.response import ok, error
from app.services import dataset_generator as dg
from app.services.rule_engine import evaluate as rule_eval
from app.services.decision_engine import evaluate as decide

bp = Blueprint("fleet", __name__)
logger = logging.getLogger(__name__)


def _load():
    try:
        return dg.load_dataset()
    except FileNotFoundError:
        return None


@bp.get("/api/fleet")
def fleet():
    df = _load()
    if df is None:
        return ok({"machines": [], "available": False})

    machines = []
    for arm_id, group in df.groupby("arm_id"):
        latest = group.iloc[-1].to_dict()
        rule_result = rule_eval(latest)

        if rule_result["has_critical"]:
            status = "EMERGENCY_STOP"
        elif rule_result["has_warning"] or latest.get("wear_label") == "Warning":
            status = "WARNING"
        elif latest.get("wear_label") == "Failure":
            status = "SCHEDULE_MAINTENANCE"
        else:
            status = "SAFE"

        machines.append({
            "arm_id":          arm_id,
            "status":          status,
            "last_timestamp":  str(latest.get("timestamp", "")),
            "wear_label":      latest.get("wear_label"),
            "temperature":     latest.get("temperature"),
            "vibration":       latest.get("vibration"),
            "torque":          latest.get("torque"),
            "rpm":             latest.get("rpm"),
            "current":         latest.get("current"),
            "pressure":        latest.get("pressure"),
            "sensor_integrity":latest.get("sensor_integrity"),
            "joint":           latest.get("joint"),
            "record_count":    len(group),
        })

    # Apply query filters
    q_status = request.args.get("status")
    q_search = request.args.get("search", "").strip().upper()
    if q_status:
        machines = [m for m in machines if m["status"] == q_status.upper()]
    if q_search:
        machines = [m for m in machines if q_search in m["arm_id"].upper()]

    return ok({"machines": machines, "total": len(machines), "available": True})


@bp.get("/api/fleet/<arm_id>")
def machine_detail(arm_id):
    df = _load()
    if df is None:
        return error("Dataset not available", 503)

    group = df[df["arm_id"] == arm_id.upper()]
    if group.empty:
        return error(f"Machine {arm_id} not found", 404)

    latest = group.iloc[-1].to_dict()
    rule_result  = rule_eval(latest)
    decision_res = decide(latest, machine_id=arm_id)

    # Joint breakdown
    joints = {}
    for joint, jdf in group.groupby("joint"):
        jlatest = jdf.iloc[-1].to_dict()
        joints[joint] = {
            "temperature": jlatest.get("temperature"),
            "vibration":   jlatest.get("vibration"),
            "torque":      jlatest.get("torque"),
            "rpm":         jlatest.get("rpm"),
            "current":     jlatest.get("current"),
            "wear_label":  jlatest.get("wear_label"),
            "record_count":len(jdf),
        }

    # Historical sensor readings (last 50)
    history = group.tail(50)[[
        "timestamp", "temperature", "pressure", "vibration",
        "rpm", "current", "torque", "wear_label", "joint"
    ]].to_dict(orient="records")

    # Recent events
    events = group[group["wear_label"] != "Normal"].tail(20)[[
        "timestamp", "joint", "wear_label", "temperature", "vibration", "torque"
    ]].to_dict(orient="records")

    return ok({
        "arm_id":        arm_id,
        "latest_reading":latest,
        "decision":      decision_res["decision"],
        "reason":        decision_res["reason"],
        "evidence":      decision_res["evidence"],
        "joints":        joints,
        "history":       history,
        "recent_events": events,
        "rule_result":   decision_res["rule_result"],
        "ml_result":     decision_res.get("ml_result"),
    })
