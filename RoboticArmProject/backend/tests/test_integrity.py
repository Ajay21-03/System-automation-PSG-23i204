"""Tests for sensor integrity / spoofing detection."""
import pytest
from app.services.integrity_service import (
    check_physical_range, check_abrupt_change,
    check_cross_sensor_consistency, full_integrity_check,
    simulate_torque_spoofing
)


def test_normal_reading_ok():
    reading = {
        "temperature": 55.0, "pressure": 4.5, "vibration": 1.5,
        "rpm": 1800.0, "current": 7.0, "torque": 40.0
    }
    result = full_integrity_check(reading, machine_id="TEST")
    assert result["overall"] == "ok"


def test_out_of_range_detected():
    reading = {"temperature": 250.0, "pressure": 4.5,
               "vibration": 1.5, "rpm": 1800.0, "current": 7.0, "torque": 40.0}
    events = check_physical_range(reading)
    assert any(e["sensor"] == "temperature" for e in events)


def test_abrupt_change_detected():
    current  = {"temperature": 90.0, "pressure": 4.5, "vibration": 1.5,
                 "rpm": 1800.0, "current": 7.0, "torque": 40.0}
    previous = {"temperature": 52.0, "pressure": 4.5, "vibration": 1.5,
                 "rpm": 1800.0, "current": 7.0, "torque": 40.0}
    events = check_abrupt_change(current, previous)
    assert any(e["sensor"] == "temperature" for e in events)


def test_cross_sensor_torque_spoofing_caught():
    """High torque + very low current should be flagged."""
    reading = {"temperature": 55.0, "pressure": 4.5, "vibration": 1.5,
               "rpm": 1800.0, "current": 1.5, "torque": 95.0}
    events = check_cross_sensor_consistency(reading)
    assert len(events) > 0


def test_spoofing_simulation_structure():
    result = simulate_torque_spoofing()
    assert "original_reading"    in result
    assert "spoofed_reading"     in result
    assert "original_integrity"  in result
    assert "spoofed_integrity"   in result
    assert "attacks_caught_by"   in result
    assert "limitations"         in result
    # Spoofed torque should be lower than original
    assert result["spoofed_reading"]["torque"] < result["original_reading"]["torque"]
