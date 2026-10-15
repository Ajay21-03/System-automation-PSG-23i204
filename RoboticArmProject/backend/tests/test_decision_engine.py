"""Tests for the final decision engine — all four outcomes."""
import pytest
from app.services.decision_engine import evaluate, demo_all_outcomes

SAFE_READING = {
    "temperature": 50.0, "pressure": 4.0, "vibration": 1.0,
    "rpm": 1600.0, "current": 5.5, "torque": 35.0, "wear_label": "Normal"
}
MONITOR_READING = {
    "temperature": 77.0, "pressure": 5.0, "vibration": 4.7,
    "rpm": 1800.0, "current": 8.0, "torque": 50.0, "wear_label": "Warning"
}
MAINTENANCE_READING = {
    "temperature": 83.0, "pressure": 6.5, "vibration": 5.5,
    "rpm": 2600.0, "current": 11.5, "torque": 89.0, "wear_label": "Failure"
}
EMERGENCY_READING = {
    "temperature": 97.0, "pressure": 9.8, "vibration": 8.0,
    "rpm": 3500.0, "current": 17.0, "torque": 116.0, "wear_label": "Failure"
}


def test_safe_decision():
    res = evaluate(SAFE_READING, machine_id="TEST")
    assert res["decision"] == "SAFE"


def test_monitor_decision():
    res = evaluate(MONITOR_READING, machine_id="TEST")
    assert res["decision"] in ("MONITOR", "SCHEDULE_MAINTENANCE", "EMERGENCY_STOP")
    # Must not be SAFE
    assert res["decision"] != "SAFE"


def test_emergency_takes_priority():
    """EMERGENCY_STOP must override everything."""
    res = evaluate(EMERGENCY_READING, machine_id="TEST", nlp_severity="info")
    assert res["decision"] == "EMERGENCY_STOP"


def test_emergency_without_ml():
    """Emergency stop must work even if ML is unavailable."""
    from unittest.mock import patch
    with patch("app.services.decision_engine.is_model_available", return_value=False):
        res = evaluate(EMERGENCY_READING, machine_id="TEST")
    assert res["decision"] == "EMERGENCY_STOP"


def test_schedule_maintenance():
    res = evaluate(MAINTENANCE_READING, machine_id="TEST", nlp_severity="critical")
    assert res["decision"] in ("SCHEDULE_MAINTENANCE", "EMERGENCY_STOP")


def test_nlp_critical_upgrades_safe():
    """NLP critical severity must upgrade SAFE → SCHEDULE_MAINTENANCE."""
    reading_no_issues = {
        "temperature": 50.0, "pressure": 4.0, "vibration": 1.0,
        "rpm": 1600.0, "current": 5.5, "torque": 35.0
    }
    res = evaluate(reading_no_issues, nlp_severity="critical", machine_id="TEST")
    assert res["decision"] in ("SCHEDULE_MAINTENANCE", "EMERGENCY_STOP")


def test_demo_all_outcomes():
    demos = demo_all_outcomes()
    assert "SAFE"                 in demos
    assert "MONITOR"              in demos
    assert "SCHEDULE_MAINTENANCE" in demos
    assert "EMERGENCY_STOP"       in demos
    assert demos["EMERGENCY_STOP"]["decision"] == "EMERGENCY_STOP"
