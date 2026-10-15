"""
Synthetic dataset generator.
Produces exactly 5,000 rows of industrial sensor data.

DISCLOSURE: This is entirely synthetic data generated for academic purposes.
Evaluation metrics obtained from this dataset do NOT indicate real-world
industrial performance.

Generation assumptions:
  - Four degradation states drive label assignment: Normal, Warning, Failure.
  - Physical relationships are modelled as:
      * Higher wear → higher temperature, vibration, torque, current.
      * Higher torque → slightly higher temperature and current draw.
      * RPM affects vibration proportionally.
  - Class distribution is intentionally unforced; realistic imbalance is preserved.
  - A fixed random seed ensures reproducibility.
  - Failure events are binary flags derived from the wear_label (Failure only),
    but are NOT fed to the ML model to prevent leakage.
  - sensor_integrity is set to 'ok' for generated data; anomalous rows are
    marked 'suspicious' at a ~2% rate to simulate real-world noise.
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone

from app.utils.config import (
    DATASET_PATH, DATA_DIR, RANDOM_SEED, DATASET_ROWS,
    ARM_IDS, JOINTS, THRESHOLDS
)


def generate(n_rows: int = DATASET_ROWS, seed: int = RANDOM_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # --- State distribution (realistic imbalance) ---
    states      = ["Normal", "Warning", "Failure"]
    state_probs = [0.65,      0.25,      0.10]
    wear_labels = rng.choice(states, size=n_rows, p=state_probs)

    # Numeric state code for parameterisation
    state_code = np.where(wear_labels == "Normal", 0,
                 np.where(wear_labels == "Warning", 1, 2))

    # Arm and joint assignment (uniform)
    arm_ids = rng.choice(ARM_IDS, size=n_rows)
    joints  = rng.choice(JOINTS,  size=n_rows)

    # --- Core sensor sampling (state-dependent distributions) ---
    # temperature °C
    temp_mean = np.where(state_code == 0, 55,
                np.where(state_code == 1, 75, 92))
    temperature = rng.normal(temp_mean, 6).clip(10, 150)

    # pressure bar
    pres_mean = np.where(state_code == 0, 4.5,
                np.where(state_code == 1, 6.5, 8.5))
    pressure = rng.normal(pres_mean, 0.8).clip(0.5, 15)

    # vibration mm/s RMS
    vib_mean = np.where(state_code == 0, 1.5,
               np.where(state_code == 1, 4.0, 7.5))
    vibration = rng.normal(vib_mean, 0.8).clip(0.0, 20)

    # RPM
    rpm_mean = np.where(state_code == 0, 1800,
               np.where(state_code == 1, 2500, 3200))
    rpm = rng.normal(rpm_mean, 150).clip(100, 4500)

    # current A
    curr_mean = np.where(state_code == 0, 7.0,
                np.where(state_code == 1, 11.0, 15.5))
    current = rng.normal(curr_mean, 1.2).clip(0.5, 25)

    # torque Nm (correlated with state + vibration)
    torque_mean = np.where(state_code == 0, 40,
                  np.where(state_code == 1, 75, 105))
    torque = (rng.normal(torque_mean, 8) + vibration * 1.5).clip(5, 180)

    # status (Day-2 original field) — string version of wear_label
    status = np.where(wear_labels == "Normal",  "normal",
             np.where(wear_labels == "Warning", "warning", "failure"))

    # failure_event — derived from wear_label (NOT used as ML feature)
    failure_event = (wear_labels == "Failure").astype(int)

    # sensor_integrity — mostly ok; ~2% suspicious
    integrity_roll = rng.random(n_rows)
    sensor_integrity = np.where(integrity_roll < 0.02, "suspicious", "ok")

    # timestamps — hourly from 90 days ago
    start_ts = datetime.now(timezone.utc) - timedelta(days=90)
    timestamps = [
        (start_ts + timedelta(hours=i)).isoformat()
        for i in range(n_rows)
    ]

    df = pd.DataFrame({
        "timestamp":        timestamps,
        "arm_id":           arm_ids,
        "joint":            joints,
        "temperature":      np.round(temperature, 2),
        "pressure":         np.round(pressure, 3),
        "vibration":        np.round(vibration, 3),
        "rpm":              np.round(rpm, 1),
        "current":          np.round(current, 3),
        "torque":           np.round(torque, 2),
        "status":           status,
        "wear_label":       wear_labels,
        "failure_event":    failure_event,
        "sensor_integrity": sensor_integrity,
    })

    return df


def save_dataset(df: pd.DataFrame = None) -> dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    if df is None:
        df = generate()
    df.to_csv(DATASET_PATH, index=False)
    dist = df["wear_label"].value_counts().to_dict()
    return {
        "rows": len(df),
        "path": DATASET_PATH,
        "class_distribution": dist,
        "columns": list(df.columns),
    }


def load_dataset() -> pd.DataFrame:
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}. Run generate first.")
    return pd.read_csv(DATASET_PATH, parse_dates=["timestamp"])
