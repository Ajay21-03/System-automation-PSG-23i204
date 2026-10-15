"""
Sensor integrity and spoofing detection module.

Implements:
  1. Physical-range checks
  2. Abrupt-change detection (temporal anomaly)
  3. Cross-sensor consistency checks
  4. Suspiciously constant-value detection

LIMITATIONS — documented honestly:
  - Cannot detect slow, gradual spoofing within plausible ranges.
  - Cannot detect coordinated multi-sensor spoofing with consistent values.
  - Not equivalent to a cryptographic sensor-authentication system.
  - False positive rate increases with genuine rapid operational changes.
"""
import logging
import math
from datetime import datetime, timezone
from app.utils.config import THRESHOLDS

logger = logging.getLogger(__name__)

# Abrupt-change thresholds (per-reading delta)
ABRUPT_CHANGE_LIMITS = {
    "temperature": 25.0,   # °C per reading
    "pressure":     3.0,   # bar
    "vibration":    5.0,   # mm/s
    "rpm":        800.0,
    "current":      8.0,   # A
    "torque":      40.0,   # Nm
}

# Constant-value detection: flag if same value repeated >= N times
CONSTANT_REPEAT_THRESHOLD = 5


def check_physical_range(reading: dict) -> list:
    """Returns list of range-violation events."""
    events = []
    checks = {
        "temperature": (THRESHOLDS["temperature_min"], THRESHOLDS["temperature_max"]),
        "pressure":    (THRESHOLDS["pressure_min"],    THRESHOLDS["pressure_max"]),
        "vibration":   (THRESHOLDS["vibration_min"],   THRESHOLDS["vibration_max"]),
        "rpm":         (THRESHOLDS["rpm_min"],          THRESHOLDS["rpm_max"]),
        "current":     (THRESHOLDS["current_min"],      THRESHOLDS["current_max"]),
        "torque":      (THRESHOLDS["torque_min"],        THRESHOLDS["torque_max"]),
    }
    for sensor, (lo, hi) in checks.items():
        val = reading.get(sensor)
        if val is None:
            continue
        try:
            val = float(val)
        except (TypeError, ValueError):
            events.append({
                "sensor":   sensor,
                "severity": "warning",
                "reason":   f"Non-numeric value: {reading.get(sensor)}",
                "value":    reading.get(sensor),
            })
            continue
        if val < lo or val > hi:
            events.append({
                "sensor":   sensor,
                "severity": "critical",
                "reason":   f"Value {val} outside physical range [{lo}, {hi}]",
                "value":    val,
            })
    return events


def check_abrupt_change(current: dict, previous: dict) -> list:
    """Compare consecutive readings for implausible jumps."""
    events = []
    if not previous:
        return events
    for sensor, limit in ABRUPT_CHANGE_LIMITS.items():
        v_curr = current.get(sensor)
        v_prev = previous.get(sensor)
        if v_curr is None or v_prev is None:
            continue
        try:
            delta = abs(float(v_curr) - float(v_prev))
        except (TypeError, ValueError):
            continue
        if delta > limit:
            events.append({
                "sensor":   sensor,
                "severity": "warning",
                "reason":   f"Abrupt change of {delta:.2f} (limit {limit}) from {v_prev} to {v_curr}",
                "value":    v_curr,
                "delta":    delta,
            })
    return events


def check_cross_sensor_consistency(reading: dict) -> list:
    """Detect physically inconsistent sensor combinations."""
    events = []
    temp    = reading.get("temperature")
    current = reading.get("current")
    torque  = reading.get("torque")
    vib     = reading.get("vibration")
    rpm     = reading.get("rpm")

    try:
        # High torque with very low current is physically implausible
        if torque is not None and current is not None:
            t, c = float(torque), float(current)
            if t > THRESHOLDS["torque_warning"] and c < 3.0:
                events.append({
                    "sensor":   "torque+current",
                    "severity": "warning",
                    "reason":   f"High torque ({t} Nm) inconsistent with very low current ({c} A) — possible torque spoofing",
                    "value":    {"torque": t, "current": c},
                })

        # High vibration with suspiciously low temperature (cold high-vibration scenario rare)
        if vib is not None and temp is not None:
            v, tp = float(vib), float(temp)
            if v > THRESHOLDS["vibration_warning"] and tp < 20.0:
                events.append({
                    "sensor":   "vibration+temperature",
                    "severity": "warning",
                    "reason":   f"High vibration ({v} mm/s) with unusually low temperature ({tp} °C) — inspect sensor",
                    "value":    {"vibration": v, "temperature": tp},
                })

        # High RPM with very low current
        if rpm is not None and current is not None:
            r, c = float(rpm), float(current)
            if r > THRESHOLDS["rpm_warning"] and c < 2.0:
                events.append({
                    "sensor":   "rpm+current",
                    "severity": "warning",
                    "reason":   f"High RPM ({r}) with very low current ({c} A) — possible current-sensor fault",
                    "value":    {"rpm": r, "current": c},
                })
    except (TypeError, ValueError) as e:
        logger.warning("Cross-sensor check error: %s", e)

    return events


# Session-level history for constant-value detection (per machine+sensor)
_history: dict = {}


def check_constant_value(reading: dict, machine_id: str = "unknown") -> list:
    """Flag sensors reporting suspiciously identical values across consecutive readings."""
    global _history
    events = []
    sensors = ["temperature", "pressure", "vibration", "rpm", "current", "torque"]
    for sensor in sensors:
        val = reading.get(sensor)
        if val is None:
            continue
        key = f"{machine_id}:{sensor}"
        hist = _history.setdefault(key, [])
        hist.append(float(val))
        if len(hist) > CONSTANT_REPEAT_THRESHOLD:
            hist.pop(0)
        if len(hist) == CONSTANT_REPEAT_THRESHOLD and len(set(hist)) == 1:
            events.append({
                "sensor":   sensor,
                "severity": "warning",
                "reason":   f"Sensor reporting identical value ({val}) for {CONSTANT_REPEAT_THRESHOLD} consecutive readings — possible sensor freeze",
                "value":    val,
            })
    return events


def full_integrity_check(reading: dict, previous: dict = None,
                          machine_id: str = "unknown") -> dict:
    """Run all integrity checks and return a unified result."""
    events = []
    events += check_physical_range(reading)
    events += check_abrupt_change(reading, previous or {})
    events += check_cross_sensor_consistency(reading)
    events += check_constant_value(reading, machine_id)

    has_critical = any(e["severity"] == "critical" for e in events)
    has_warning  = any(e["severity"] == "warning"  for e in events)

    if has_critical:
        overall = "compromised"
    elif has_warning:
        overall = "suspicious"
    else:
        overall = "ok"

    return {
        "overall":    overall,
        "events":     events,
        "event_count": len(events),
        "has_critical": has_critical,
        "has_warning":  has_warning,
        "checked_at":   datetime.now(timezone.utc).isoformat(),
        "machine_id":   machine_id,
    }


def simulate_torque_spoofing(arm_id: str = "ARM-001",
                              joint: str = "shoulder") -> dict:
    """
    Demonstrate a torque-spoofing scenario.
    An attacker falsifies torque to appear normal while other sensors show distress.
    This function operates on a COPY — the real dataset is NOT modified.

    Returns:
      original_reading  — real values (simulated genuine failure)
      spoofed_reading   — attacker-modified reading
      detection_result  — which checks caught the spoofing
    """
    original = {
        "arm_id":      arm_id,
        "joint":       joint,
        "temperature": 91.0,
        "pressure":    8.8,
        "vibration":   7.2,
        "rpm":         3100.0,
        "current":     15.8,
        "torque":      112.0,   # genuinely critical
    }

    spoofed = dict(original)
    spoofed["torque"] = 38.0   # attacker makes torque look normal

    original_check = full_integrity_check(dict(original), machine_id=arm_id)
    spoofed_check  = full_integrity_check(dict(spoofed),  previous=original, machine_id=arm_id)

    return {
        "scenario":         "Torque-Spoofing Attack Simulation",
        "disclaimer":       "This operates on simulated data only. The real dataset is not modified.",
        "original_reading": original,
        "spoofed_reading":  spoofed,
        "original_integrity": original_check,
        "spoofed_integrity":  spoofed_check,
        "attacks_caught_by":  [e["reason"] for e in spoofed_check["events"]],
        "limitations": [
            "Slow gradual spoofing within plausible ranges cannot be detected by these checks.",
            "Coordinated multi-sensor spoofing with consistent values may evade cross-sensor checks.",
            "This is not a cryptographic or hardware-authenticated sensor system.",
        ],
    }
