"""
Final Decision Engine — four-outcome determinator.

Priority (strict):
  1. EMERGENCY_STOP — any confirmed dangerous sensor reading (rule-based)
  2. SCHEDULE_MAINTENANCE — significant wear / serious maintenance evidence
  3. MONITOR — mild warnings, unresolved anomalies, suspicious readings
  4. SAFE — valid readings, no significant warnings

The safety layer (rule engine) operates independently of ML.
A missing or failed ML model does NOT disable emergency-stop logic.
Invalid inputs do NOT automatically yield SAFE.
"""
import logging
from datetime import datetime, timezone

from app.services.rule_engine    import evaluate as rule_evaluate
from app.services.ml_service     import predict as ml_predict, is_model_available
from app.services.integrity_service import full_integrity_check

logger = logging.getLogger(__name__)

DECISIONS = ["SAFE", "MONITOR", "SCHEDULE_MAINTENANCE", "EMERGENCY_STOP"]


def evaluate(reading: dict, previous_reading: dict = None,
             nlp_severity: str = None, machine_id: str = "unknown") -> dict:
    """
    Evaluate one reading and return a final decision with full evidence.

    Parameters
    ----------
    reading          : sensor reading dict
    previous_reading : preceding reading for abrupt-change checks
    nlp_severity     : severity string from maintenance log NLP ('critical'|'warning'|'info'|None)
    machine_id       : identifier for logging

    Returns
    -------
    {
      decision, reason, rule_result, ml_result, integrity_result,
      nlp_contribution, evidence, timestamp
    }
    """
    evidence      = []
    decision      = "SAFE"
    reason_parts  = []

    # ------------------------------------------------------------------
    # STEP 1 — Integrity check (pre-validation)
    # ------------------------------------------------------------------
    integrity_result = full_integrity_check(
        reading, previous=previous_reading or {}, machine_id=machine_id
    )
    if integrity_result["has_critical"]:
        evidence.append("Sensor integrity: COMPROMISED — values outside physical bounds.")
        # Don't return SAFE; treat as MONITOR at minimum
        if decision in ("SAFE",):
            decision = "MONITOR"
            reason_parts.append("Sensor integrity compromised.")
    elif integrity_result["has_warning"]:
        evidence.append("Sensor integrity: SUSPICIOUS — anomalous reading pattern.")
        if decision == "SAFE":
            decision = "MONITOR"
            reason_parts.append("Sensor integrity suspicious.")

    # ------------------------------------------------------------------
    # STEP 2 — Rule-based safety check (MUST run; highest authority)
    # ------------------------------------------------------------------
    rule_result = rule_evaluate(reading)

    if rule_result["has_critical"]:
        decision = "EMERGENCY_STOP"
        for r in rule_result["triggered_rules"]:
            if r["severity"] == "critical":
                evidence.append(
                    f"RULE [{r['rule_id']}] {r['name']}: "
                    f"{r['sensor']}={r['value']} ≥ {r['threshold']}"
                )
        reason_parts.insert(0, "Critical safety threshold exceeded — EMERGENCY STOP.")

    elif rule_result["has_warning"]:
        evidence.append("Rule engine: Warning-level condition detected.")
        if decision not in ("EMERGENCY_STOP",):
            decision = "MONITOR"
            reason_parts.append("Warning-level rule triggered.")

    # ------------------------------------------------------------------
    # STEP 3 — ML prediction (advisory only)
    # ------------------------------------------------------------------
    ml_result = None
    ml_class  = None

    if is_model_available():
        try:
            ml_result = ml_predict(reading)
            ml_class  = ml_result["predicted_class"]
            evidence.append(f"ML prediction: {ml_class} "
                            f"(confidence {max(ml_result['probabilities'].values()):.1%})")

            # ML can upgrade decision but NOT downgrade an EMERGENCY_STOP
            if ml_class == "Failure" and decision not in ("EMERGENCY_STOP",):
                decision = "SCHEDULE_MAINTENANCE"
                reason_parts.append("ML predicts Failure — schedule maintenance.")
            elif ml_class == "Warning" and decision == "SAFE":
                decision = "MONITOR"
                reason_parts.append("ML predicts Warning condition.")
            # ml_class == "Normal" → does NOT override rule-based decisions

        except Exception as exc:
            logger.warning("ML predict failed during decision: %s", exc)
            ml_result = {"error": str(exc), "model_available": False}
            evidence.append(f"ML prediction unavailable: {exc}")
    else:
        evidence.append("ML model not loaded — rule-based decision only.")

    # ------------------------------------------------------------------
    # STEP 4 — NLP maintenance note contribution
    # ------------------------------------------------------------------
    nlp_contribution = None
    if nlp_severity == "critical" and decision not in ("EMERGENCY_STOP",):
        decision = "SCHEDULE_MAINTENANCE"
        nlp_contribution = "critical"
        reason_parts.append("Maintenance log contains critical indicators.")
        evidence.append("Maintenance log NLP: critical severity indicators detected.")
    elif nlp_severity == "warning" and decision == "SAFE":
        decision = "MONITOR"
        nlp_contribution = "warning"
        reason_parts.append("Maintenance log contains warning indicators.")
        evidence.append("Maintenance log NLP: warning severity indicators detected.")

    # ------------------------------------------------------------------
    # STEP 5 — Wear-label promotion (data-driven, no emergency override)
    # ------------------------------------------------------------------
    wear_label = reading.get("wear_label")
    if wear_label == "Failure" and decision not in ("EMERGENCY_STOP", "SCHEDULE_MAINTENANCE"):
        decision = "SCHEDULE_MAINTENANCE"
        reason_parts.append("Sensor data wear label indicates Failure.")
        evidence.append("Data wear_label: Failure.")
    elif wear_label == "Warning" and decision == "SAFE":
        decision = "MONITOR"

    # ------------------------------------------------------------------
    # FINAL
    # ------------------------------------------------------------------
    if not reason_parts:
        reason_parts = ["All sensors within normal operating parameters."]

    return {
        "decision":           decision,
        "reason":             " | ".join(reason_parts),
        "rule_result":        rule_result,
        "ml_result":          ml_result,
        "integrity_result":   integrity_result,
        "nlp_contribution":   nlp_contribution,
        "evidence":           evidence,
        "machine_id":         machine_id,
        "evaluated_at":       datetime.now(timezone.utc).isoformat(),
    }


def demo_all_outcomes() -> dict:
    """Return one reproducible demonstration for each of the four decisions."""
    safe_reading = {
        "temperature": 52.0, "pressure": 4.2, "vibration": 1.1,
        "rpm": 1750.0, "current": 6.5, "torque": 38.0, "wear_label": "Normal"
    }
    monitor_reading = {
        "temperature": 76.0, "pressure": 5.0, "vibration": 4.6,
        "rpm": 1800.0, "current": 8.0, "torque": 55.0, "wear_label": "Warning"
    }
    maintenance_reading = {
        "temperature": 83.0, "pressure": 6.8, "vibration": 5.5,
        "rpm": 2600.0, "current": 11.5, "torque": 88.0, "wear_label": "Failure"
    }
    emergency_reading = {
        "temperature": 97.0, "pressure": 9.8, "vibration": 8.0,
        "rpm": 3500.0, "current": 17.0, "torque": 115.0, "wear_label": "Failure"
    }

    return {
        "SAFE":                evaluate(safe_reading,        machine_id="DEMO-SAFE"),
        "MONITOR":             evaluate(monitor_reading,     machine_id="DEMO-MONITOR"),
        "SCHEDULE_MAINTENANCE":evaluate(maintenance_reading, machine_id="DEMO-MAINT",
                                        nlp_severity="critical"),
        "EMERGENCY_STOP":      evaluate(emergency_reading,   machine_id="DEMO-EMERG"),
    }
