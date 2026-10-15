"""Dashboard summary and trend endpoints."""
import os
import logging
from flask import Blueprint, request
from app.utils.response import ok, error
from app.utils.config import DATASET_PATH, ARM_IDS, THRESHOLDS
from app.services import dataset_generator as dg
from app.services.ml_service import is_model_available, get_metrics
from app.services.rule_engine import evaluate as rule_eval
from app.services.persistence import maintenance_case_count

bp = Blueprint("dashboard", __name__)
logger = logging.getLogger(__name__)


def _load_df():
    try:
        return dg.load_dataset()
    except FileNotFoundError:
        return None


@bp.get("/api/dashboard/summary")
def summary():
    df = _load_df()
    if df is None:
        return ok({
            "dataset_available": False,
            "model_available":   is_model_available(),
            "kpis": {},
            "message": "Dataset not generated yet. Visit /data-lab to generate it.",
        })

    total = len(df)
    dist  = df["wear_label"].value_counts().to_dict()

    # Machine-level aggregation
    latest = df.groupby("arm_id").last().reset_index()
    machine_statuses = {}
    emergency_arms   = []
    warning_arms     = []

    for _, row in latest.iterrows():
        reading = row.to_dict()
        result  = rule_eval(reading)
        arm     = row["arm_id"]
        if result["has_critical"]:
            machine_statuses[arm] = "EMERGENCY_STOP"
            emergency_arms.append(arm)
        elif result["has_warning"] or row.get("wear_label") == "Warning":
            machine_statuses[arm] = "WARNING"
            warning_arms.append(arm)
        elif row.get("wear_label") == "Failure":
            machine_statuses[arm] = "SCHEDULE_MAINTENANCE"
        else:
            machine_statuses[arm] = "SAFE"

    normal_count = sum(1 for v in machine_statuses.values() if v == "SAFE")
    maint_count  = maintenance_case_count()

    # Sensor integrity summary
    integrity_ok = int((df["sensor_integrity"] == "ok").sum())
    integrity_susp = int((df["sensor_integrity"] == "suspicious").sum())

    kpis = {
        "total_machines":         len(ARM_IDS),
        "monitored_records":      total,
        "normal_machines":        normal_count,
        "warning_machines":       len(warning_arms),
        "emergency_stops":        len(emergency_arms),
        "predicted_maintenance":  int(dist.get("Failure", 0)),
        "sensor_integrity_alerts":integrity_susp,
        "maintenance_cases_open": maint_count,
        "class_distribution":     dist,
        "machine_statuses":       machine_statuses,
        "emergency_arms":         emergency_arms,
    }

    return ok({
        "dataset_available":    True,
        "model_available":      is_model_available(),
        "kpis":                 kpis,
        "dataset_rows":         total,
    })


@bp.get("/api/dashboard/trends")
def trends():
    df = _load_df()
    if df is None:
        return ok({"available": False, "series": []})

    # Resample to daily counts for trend charts
    df["date"] = df["timestamp"].dt.date.astype(str)
    daily = df.groupby(["date", "wear_label"]).size().unstack(fill_value=0).reset_index()

    series = []
    for _, row in daily.iterrows():
        entry = {"date": row["date"]}
        for lbl in ["Normal", "Warning", "Failure"]:
            entry[lbl] = int(row.get(lbl, 0))
        series.append(entry)

    # Sensor averages by arm
    sensor_avgs = (
        df.groupby("arm_id")[["temperature", "pressure", "vibration",
                               "rpm", "current", "torque"]]
        .mean().round(2).reset_index().to_dict(orient="records")
    )

    # Recent events (last 50 rows with non-normal status)
    alerts_df = df[df["wear_label"] != "Normal"].tail(50)
    recent_events = alerts_df[[
        "timestamp", "arm_id", "joint", "wear_label",
        "temperature", "vibration", "torque"
    ]].to_dict(orient="records")

    return ok({
        "available":    True,
        "trend_series": series,
        "sensor_avgs":  sensor_avgs,
        "recent_events":recent_events,
    })
