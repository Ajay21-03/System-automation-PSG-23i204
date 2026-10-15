"""
Day-1 / Day-2 Rule-Based Safety Engine.
Implements the Sense → Think → Act → Log workflow.

IMPORTANT: This safety layer is independent of the ML model.
Emergency-stop logic runs even when the ML model is unavailable.

All thresholds are simulation assumptions, not certified safety limits.
"""
import logging
from datetime import datetime, timezone
from app.utils.config import THRESHOLDS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rule definitions
# ---------------------------------------------------------------------------
RULES = [
    {
        "id": "R001",
        "name": "Critical Temperature",
        "description": "Joint temperature exceeds critical threshold — risk of thermal damage.",
        "sensor": "temperature",
        "threshold": THRESHOLDS["temperature_critical"],
        "operator": ">=",
        "severity": "critical",
        "action": "EMERGENCY_STOP",
        "enabled": True,
        "safety_critical": True,
    },
    {
        "id": "R002",
        "name": "Warning Temperature",
        "description": "Joint temperature in elevated warning zone.",
        "sensor": "temperature",
        "threshold": THRESHOLDS["temperature_warning"],
        "operator": ">=",
        "severity": "warning",
        "action": "MONITOR",
        "enabled": True,
        "safety_critical": False,
    },
    {
        "id": "R003",
        "name": "Critical Vibration",
        "description": "Vibration exceeds critical level — possible mechanical failure.",
        "sensor": "vibration",
        "threshold": THRESHOLDS["vibration_critical"],
        "operator": ">=",
        "severity": "critical",
        "action": "EMERGENCY_STOP",
        "enabled": True,
        "safety_critical": True,
    },
    {
        "id": "R004",
        "name": "Warning Vibration",
        "description": "Vibration elevated — possible early bearing wear.",
        "sensor": "vibration",
        "threshold": THRESHOLDS["vibration_warning"],
        "operator": ">=",
        "severity": "warning",
        "action": "MONITOR",
        "enabled": True,
        "safety_critical": False,
    },
    {
        "id": "R005",
        "name": "Critical Pressure",
        "description": "Hydraulic/pneumatic pressure critically high.",
        "sensor": "pressure",
        "threshold": THRESHOLDS["pressure_critical"],
        "operator": ">=",
        "severity": "critical",
        "action": "EMERGENCY_STOP",
        "enabled": True,
        "safety_critical": True,
    },
    {
        "id": "R006",
        "name": "Warning Pressure",
        "description": "Pressure elevated beyond normal operating range.",
        "sensor": "pressure",
        "threshold": THRESHOLDS["pressure_warning"],
        "operator": ">=",
        "severity": "warning",
        "action": "MONITOR",
        "enabled": True,
        "safety_critical": False,
    },
    {
        "id": "R007",
        "name": "Critical Torque",
        "description": "Torque exceeds critical limit — structural damage risk.",
        "sensor": "torque",
        "threshold": THRESHOLDS["torque_critical"],
        "operator": ">=",
        "severity": "critical",
        "action": "EMERGENCY_STOP",
        "enabled": True,
        "safety_critical": True,
    },
    {
        "id": "R008",
        "name": "Warning Torque",
        "description": "Torque in elevated warning zone — inspect joint.",
        "sensor": "torque",
        "threshold": THRESHOLDS["torque_warning"],
        "operator": ">=",
        "severity": "warning",
        "action": "MONITOR",
        "enabled": True,
        "safety_critical": False,
    },
    {
        "id": "R009",
        "name": "Critical RPM",
        "description": "RPM exceeds safe operating speed.",
        "sensor": "rpm",
        "threshold": THRESHOLDS["rpm_critical"],
        "operator": ">=",
        "severity": "critical",
        "action": "EMERGENCY_STOP",
        "enabled": True,
        "safety_critical": True,
    },
    {
        "id": "R010",
        "name": "Critical Current",
        "description": "Motor current draw critically high — possible motor failure.",
        "sensor": "current",
        "threshold": THRESHOLDS["current_critical"],
        "operator": ">=",
        "severity": "critical",
        "action": "EMERGENCY_STOP",
        "enabled": True,
        "safety_critical": True,
    },
]

# In-memory trigger tracking (per session; reset on restart)
_trigger_counts: dict = {r["id"]: 0 for r in RULES}
_last_triggered: dict = {r["id"]: None for r in RULES}


def _evaluate_rule(rule: dict, reading: dict) -> bool:
    """Apply a single rule to a reading dict. Returns True if triggered."""
    sensor = rule["sensor"]
    val = reading.get(sensor)
    if val is None:
        return False
    try:
        val = float(val)
    except (TypeError, ValueError):
        return False
    threshold = rule["threshold"]
    op = rule["operator"]
    if op == ">=":
        return val >= threshold
    if op == ">":
        return val > threshold
    if op == "<=":
        return val <= threshold
    if op == "<":
        return val < threshold
    return False


def evaluate(reading: dict) -> dict:
    """
    SENSE → THINK → ACT → LOG for one sensor reading.

    Returns:
      {
        triggered_rules: list of triggered rule IDs + info,
        has_critical:    bool,
        has_warning:     bool,
        rule_action:     highest-priority action string,
        evidence:        list of human-readable strings,
      }
    """
    triggered = []
    has_critical = False
    has_warning  = False

    for rule in RULES:
        if not rule["enabled"]:
            continue
        if _evaluate_rule(rule, reading):
            triggered.append({
                "rule_id":   rule["id"],
                "name":      rule["name"],
                "sensor":    rule["sensor"],
                "severity":  rule["severity"],
                "action":    rule["action"],
                "threshold": rule["threshold"],
                "value":     reading.get(rule["sensor"]),
            })
            # Update session counters
            _trigger_counts[rule["id"]] += 1
            _last_triggered[rule["id"]] = datetime.now(timezone.utc).isoformat()

            if rule["severity"] == "critical":
                has_critical = True
            elif rule["severity"] == "warning":
                has_warning = True

    # Determine highest-priority action
    if has_critical:
        rule_action = "EMERGENCY_STOP"
    elif has_warning:
        rule_action = "MONITOR"
    else:
        rule_action = None  # no rule triggered

    evidence = [
        f"{t['name']}: {t['sensor']}={t['value']} (threshold >={t['threshold']})"
        for t in triggered
    ]

    return {
        "triggered_rules": triggered,
        "has_critical":    has_critical,
        "has_warning":     has_warning,
        "rule_action":     rule_action,
        "evidence":        evidence,
    }


def get_rules_with_stats() -> list:
    result = []
    for rule in RULES:
        r = dict(rule)
        r["trigger_count"] = _trigger_counts.get(rule["id"], 0)
        r["last_triggered"] = _last_triggered.get(rule["id"])
        result.append(r)
    return result
