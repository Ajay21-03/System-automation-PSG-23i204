"""
DAY 1 ┬╖ HANDS-ON ΓÇö Build Your Rule Engine
23IF02 System Automation

Work through the TODOs in order. Each one matches a step on the
"Hands-on ┬╖ Build Your Rule Engine" slide. Run this file after each
step to see your progress:

    python hands_on_starter.py

Need the answer? See hands_on_solution.py ΓÇö but try it yourself first.
"""

import random
import time

LOG_FILE = "day1_log.txt"


# ---------------------------------------------------------------------------
# STEP 1 ΓÇö Generate simulated sensor data
# ---------------------------------------------------------------------------
def generate_sensor_data():
    """Return a dict with at least 'temperature', 'pressure', 'vibration'."""
    # TODO: fill in realistic random values, e.g. temperature 50-95 (deg C)
    return {
        "temperature": random.randint(50, 95),
        "pressure": random.randint(30, 50),
        "vibration": round(random.uniform(0.1, 5.0), 2),
        "current": random.randint(5, 25),  # STEP 6 ΓÇö Second sensor
    }
    # STRETCH GOAL (after the 8 steps below all work): real sensors aren't
    # perfectly clean. Try making one field randomly return None (a
    # dropout) or spike far outside its normal range every so often, then
    # update evaluate_rules() so a dropout doesn't crash your engine.


# ---------------------------------------------------------------------------
# STEP 2 ΓÇö Write your first automation rules
# STEP 7 ΓÇö Add a rule of your own (add another dict to this list)
# STEP 8 ΓÇö Add one priority rule (lower "priority" number checked first)
# ---------------------------------------------------------------------------
RULES = [
    {
        "name": "HIGH_TEMP",
        "priority": 1,
        "condition": lambda r: r["temperature"] > 80,
        "action": "STOP_MACHINE",
    },
    {
        "name": "HIGH_VIBRATION",
        "priority": 2,
        "condition": lambda r: r["vibration"] > 4.0,
        "action": "INSPECT_MACHINE",
    },
    {
        "name": "HIGH_PRESSURE",
        "priority": 3,
        "condition": lambda r: r["pressure"] > 45,
        "action": "REDUCE_PRESSURE",
    },
    {
        "name": "HIGH_CURRENT",  # STEP 6 ΓÇö Rule using the second sensor
        "priority": 4,
        "condition": lambda r: r["current"] > 20,
        "action": "CHECK_ELECTRICAL_SYSTEM",
    },
    {
        "name": "CUSTOM_RULE",  # STEP 7 ΓÇö Your own rule
        "priority": 5,
        "condition": lambda r: (
            r["temperature"] > 70 and r["vibration"] > 3.0
        ),
        "action": "PERFORM_MAINTENANCE",
    },
    {
        "name": "PRIORITY_EMERGENCY",  # STEP 8 ΓÇö Highest-priority rule
        "priority": 0,
        "condition": lambda r: (
            r["temperature"] > 90 or r["vibration"] > 4.8
        ),
        "action": "EMERGENCY_SHUTDOWN",
    },
]


# ---------------------------------------------------------------------------
# STEP 3 ΓÇö Detect machine state from the rules
# ---------------------------------------------------------------------------
def evaluate_rules(reading, rules):
    """Return (rule_name, action) for the first matching rule, checked in
    priority order (lowest number first). If nothing matches, return
    ("NO_RULE_FIRED", "CONTINUE_NORMAL")."""
    # TODO: sort `rules` by priority, then check each rule's condition(reading)
    sorted_rules = sorted(rules, key=lambda rule: rule["priority"])

    for rule in sorted_rules:
        try:
            if rule["condition"](reading):
                return rule["name"], rule["action"]
        except (KeyError, TypeError):
            # Handle missing or invalid sensor readings safely.
            continue

    return "NO_RULE_FIRED", "CONTINUE_NORMAL"


# ---------------------------------------------------------------------------
# STEP 4 ΓÇö Trigger an action when a rule fires
# ---------------------------------------------------------------------------
def take_action(action):
    """Return a human-readable string describing what happens for this action."""
    # TODO: map action names (e.g. "STOP_MACHINE") to a message
    actions = {
        "STOP_MACHINE": "Machine stopped due to high temperature.",
        "INSPECT_MACHINE": "Warning: Inspect the machine for excessive vibration.",
        "REDUCE_PRESSURE": "Warning: Reduce machine pressure.",
        "CHECK_ELECTRICAL_SYSTEM": "Warning: Check the electrical system.",
        "PERFORM_MAINTENANCE": "Maintenance required due to combined sensor readings.",
        "EMERGENCY_SHUTDOWN": "EMERGENCY: Machine shutdown triggered!",
        "CONTINUE_NORMAL": "All sensor readings are within normal limits. Continue operation.",
    }

    return actions.get(action, f"(no handler yet for action: {action})")


# ---------------------------------------------------------------------------
# STEP 5 ΓÇö Log every decision made
# ---------------------------------------------------------------------------
def log_decision(reading, rule_name, action):
    """Append one line to LOG_FILE with the reading, rule fired, and action."""
    # TODO: open(LOG_FILE, "a") and write a line
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(
            f"{timestamp} | Reading: {reading} | "
            f"Rule: {rule_name} | Action: {action}\n"
        )


# ---------------------------------------------------------------------------
# STEP 6 ΓÇö Add a second sensor to the system
# TODO: add e.g. "current" to generate_sensor_data(), then use it in a rule
# ---------------------------------------------------------------------------


def main():
    for tick in range(1, 11):
        reading = generate_sensor_data()
        rule_name, action = evaluate_rules(reading, RULES)
        outcome = take_action(action)

        print(f"[Tick {tick:02d}] SENSE -> {reading}")
        print(f"           THINK -> {rule_name}")
        print(f"           ACT   -> {outcome}\n")

        log_decision(reading, rule_name, action)
        time.sleep(0.2)


if __name__ == "__main__":
    main()
