"""Live/historical sensor monitoring endpoint."""
from flask import Blueprint, request
from app.utils.response import ok, error
from app.services import dataset_generator as dg
from app.utils.config import THRESHOLDS, ARM_IDS, JOINTS

bp = Blueprint("monitoring", __name__)


@bp.get("/api/monitoring/readings")
def readings():
    try:
        df = dg.load_dataset()
    except FileNotFoundError:
        return ok({"available": False, "readings": [], "mode": "no_data"})

    arm_id  = request.args.get("arm_id")
    joint   = request.args.get("joint")
    sensor  = request.args.get("sensor")
    limit   = min(int(request.args.get("limit", 100)), 500)

    filtered = df.copy()
    if arm_id:
        filtered = filtered[filtered["arm_id"] == arm_id.upper()]
    if joint:
        filtered = filtered[filtered["joint"] == joint.lower()]

    filtered = filtered.tail(limit)
    readings_list = filtered[[
        "timestamp", "arm_id", "joint",
        "temperature", "pressure", "vibration",
        "rpm", "current", "torque",
        "wear_label", "sensor_integrity"
    ]].to_dict(orient="records")

    # Apply thresholds for client-side highlighting
    for r in readings_list:
        r["threshold_flags"] = {
            "temperature": _flag(r.get("temperature"), "temperature"),
            "pressure":    _flag(r.get("pressure"),    "pressure"),
            "vibration":   _flag(r.get("vibration"),   "vibration"),
            "rpm":         _flag(r.get("rpm"),         "rpm"),
            "current":     _flag(r.get("current"),     "current"),
            "torque":      _flag(r.get("torque"),      "torque"),
        }

    return ok({
        "available":    True,
        "mode":         "historical_replay",
        "mode_label":   "Historical Data Replay (not live hardware acquisition)",
        "readings":     readings_list,
        "count":        len(readings_list),
        "thresholds":   THRESHOLDS,
        "available_arms":  ARM_IDS,
        "available_joints":JOINTS,
    })


def _flag(val, sensor):
    if val is None:
        return "unknown"
    try:
        v = float(val)
    except (TypeError, ValueError):
        return "invalid"
    if v >= THRESHOLDS.get(f"{sensor}_critical", float("inf")):
        return "critical"
    if v >= THRESHOLDS.get(f"{sensor}_warning", float("inf")):
        return "warning"
    return "normal"
