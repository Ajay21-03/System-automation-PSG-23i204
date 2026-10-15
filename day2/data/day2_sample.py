"""
DAY 2 ┬╖ Industrial Sensor Telemetry Generator
23IF02 System Automation

Generates synthetic industrial sensor records matching the schema
and characteristics of day2_sample.csv:
- Features: temperature, pressure, vibration, current, rpm, state
- Machine States:
    1. NORMAL          - All sensor readings within nominal limits
    2. OVERHEATING     - Temperature > 70.0 ┬░C
    3. LOW_PRESSURE    - Pressure < 4.0 bar
    4. HIGH_VIBRATION  - Vibration > 3.5 mm/s
    5. MOTOR_OVERLOAD  - Current > 16.0 A

Saves generated records to 'day2_sample.csv' in the same directory.
"""

import csv
from pathlib import Path
import random

DATA_DIR = Path(__file__).resolve().parent
CSV_FILE = DATA_DIR / "day2_sample.csv"

NUM_RECORDS = 250
RANDOM_SEED = 42
random.seed(RANDOM_SEED)


def get_machine_status(temperature, pressure, vibration, current, rpm):
    """Determine machine state dynamically based on physical thresholds."""
    if temperature > 70.0:
        return "OVERHEATING"
    elif pressure < 4.0:
        return "LOW_PRESSURE"
    elif vibration > 3.5:
        return "HIGH_VIBRATION"
    elif current > 16.0:
        return "MOTOR_OVERLOAD"
    else:
        return "NORMAL"


def generate_sensor_data(tick):
    """Generate realistic sensor readings for one record based on operating condition."""
    # Simulation condition selection matching dataset proportions:
    # ~62% Normal, ~11% Motor Overload, ~10% Overheating, ~9% Low Pressure, ~8% High Vibration
    condition = random.choices(
        ["NORMAL", "OVERHEATING", "HIGH_VIBRATION", "MOTOR_OVERLOAD", "LOW_PRESSURE"],
        weights=[62, 10, 8, 11, 9],
        k=1,
    )[0]

    # Baseline nominal values (NORMAL state)
    temperature = round(random.uniform(55.0, 70.0), 2)
    pressure = round(random.uniform(4.0, 6.5), 2)
    vibration = round(random.uniform(1.0, 3.5), 2)
    current = round(random.uniform(8.0, 16.0), 2)
    rpm = random.randint(1400, 2200)

    # Inject specific anomalies based on the selected condition
    if condition == "OVERHEATING":
        temperature = round(random.uniform(70.5, 98.0), 2)

    elif condition == "LOW_PRESSURE":
        pressure = round(random.uniform(1.0, 3.8), 2)

    elif condition == "HIGH_VIBRATION":
        vibration = round(random.uniform(3.6, 9.8), 2)

    elif condition == "MOTOR_OVERLOAD":
        current = round(random.uniform(16.2, 29.0), 2)

    # Assign state dynamically using threshold rules
    state = get_machine_status(temperature, pressure, vibration, current, rpm)

    return {
        "temperature": temperature,
        "pressure": pressure,
        "vibration": vibration,
        "current": current,
        "rpm": rpm,
        "state": state,
    }


def save_to_csv(records, filename):
    """Save generated records into CSV file."""
    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "temperature",
        "pressure",
        "vibration",
        "current",
        "rpm",
        "state",
    ]

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def main():
    records = []

    for tick in range(1, NUM_RECORDS + 1):
        reading = generate_sensor_data(tick)
        records.append(reading)

        print(
            f"[Record {tick:03d}] "
            f"State: {reading['state']:15s} | "
            f"Temp: {reading['temperature']:5.2f}┬░C | "
            f"Pres: {reading['pressure']:4.2f} bar | "
            f"Vib: {reading['vibration']:4.2f} mm/s | "
            f"Current: {reading['current']:5.2f} A | "
            f"RPM: {reading['rpm']:4d}"
        )

    save_to_csv(records, CSV_FILE)

    # Summary distribution
    state_counts = {}
    for r in records:
        state_counts[r["state"]] = state_counts.get(r["state"], 0) + 1

    print(f"\n[+] Successfully saved {len(records)} records to: {CSV_FILE}")
    print("\nState distribution:")
    for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    {state:15s}: {count:3d} records ({count / len(records) * 100:.1f}%)")


if __name__ == "__main__":
    main()
