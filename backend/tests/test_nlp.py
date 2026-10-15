"""Tests for maintenance log NLP analysis."""
import pytest
from app.services.nlp_service import analyze_note


def test_vibration_detected():
    result = analyze_note("ARM-001 shoulder showing abnormal vibration")
    assert "vibration" in result["detected_terms"]
    assert result["relevant"] is True


def test_negation_handling():
    result = analyze_note("No vibration detected, all normal")
    assert "vibration" not in result["detected_terms"]
    assert "vibration" in result["negated_terms"]


def test_grinding_severity_critical():
    result = analyze_note("Grinding noise from elbow joint")
    assert result["severity"] == "critical"


def test_routine_note_not_relevant():
    result = analyze_note("Routine scheduled maintenance inspection completed successfully")
    assert result["relevant"] is False


def test_arm_id_extraction():
    result = analyze_note("ARM-003 wrist joint overheat")
    assert result["arm_id"] is not None
    assert "003" in result["arm_id"]


def test_joint_extraction():
    result = analyze_note("Elbow joint torque irregular")
    assert result["joint"] == "elbow"


def test_failure_term_detected():
    result = analyze_note("ARM-002 servo driver fault alarm")
    assert "failure" in result["detected_terms"]
    assert result["relevant"] is True
