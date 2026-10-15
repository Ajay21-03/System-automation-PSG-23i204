"""Tests for the rule-based safety engine."""
import pytest
from app.services.rule_engine import evaluate


NORMAL = {
    "temperature": 52.0, "pressure": 4.0, "vibration": 1.2,
    "rpm": 1700.0, "current": 6.0, "torque": 38.0
}
WARNING_TEMP = {**NORMAL, "temperature": 78.0}
CRITICAL_TEMP = {**NORMAL, "temperature": 96.0}
CRITICAL_VIB  = {**NORMAL, "vibration": 7.5}
CRITICAL_TORQUE = {**NORMAL, "torque": 115.0}


def test_normal_no_trigger():
    result = evaluate(NORMAL)
    assert not result["has_critical"]
    assert not result["has_warning"]
    assert result["rule_action"] is None


def test_warning_temperature():
    result = evaluate(WARNING_TEMP)
    assert result["has_warning"]
    assert not result["has_critical"]
    assert result["rule_action"] == "MONITOR"


def test_critical_temperature_emergency():
    result = evaluate(CRITICAL_TEMP)
    assert result["has_critical"]
    assert result["rule_action"] == "EMERGENCY_STOP"


def test_critical_vibration_emergency():
    result = evaluate(CRITICAL_VIB)
    assert result["has_critical"]
    assert result["rule_action"] == "EMERGENCY_STOP"


def test_critical_torque_emergency():
    result = evaluate(CRITICAL_TORQUE)
    assert result["has_critical"]
    assert result["rule_action"] == "EMERGENCY_STOP"


def test_missing_sensor_does_not_trigger():
    """Missing sensor value must not crash or falsely trigger."""
    result = evaluate({"temperature": None, "pressure": 4.0})
    assert result["rule_action"] is None
