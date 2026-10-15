"""
Central configuration — thresholds, paths, constants.
All threshold values are documented as simulation assumptions,
NOT certified industrial safety limits.
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR   = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models_ml")

DATASET_PATH        = os.path.join(DATA_DIR, "sensor_data.csv")
MAINTENANCE_LOG_PATH= os.path.join(DATA_DIR, "maintenance_log.txt")
MODEL_PATH          = os.path.join(MODELS_DIR, "random_forest_model.joblib")
METRICS_PATH        = os.path.join(MODELS_DIR, "model_metrics.json")
DB_PATH             = os.path.join(DATA_DIR, "iicc.db")
AUDIT_LOG_PATH      = os.path.join(DATA_DIR, "audit_log.jsonl")

RANDOM_SEED = 42
DATASET_ROWS = 5000

# --- SIMULATION THRESHOLDS (not certified engineering limits) ---
THRESHOLDS = {
    # temperature °C
    "temperature_warning":   75.0,
    "temperature_critical":  95.0,
    # pressure bar
    "pressure_warning":      7.5,
    "pressure_critical":     9.5,
    # vibration mm/s RMS
    "vibration_warning":     4.5,
    "vibration_critical":    7.0,
    # RPM
    "rpm_warning":           2800.0,
    "rpm_critical":          3400.0,
    # current A
    "current_warning":       12.0,
    "current_critical":      16.0,
    # torque Nm
    "torque_warning":        85.0,
    "torque_critical":       110.0,
    # physical plausible ranges (outside = integrity alert)
    "temperature_min":  -10.0,
    "temperature_max":  200.0,
    "pressure_min":       0.0,
    "pressure_max":      20.0,
    "vibration_min":      0.0,
    "vibration_max":     30.0,
    "rpm_min":            0.0,
    "rpm_max":         5000.0,
    "current_min":        0.0,
    "current_max":       30.0,
    "torque_min":         0.0,
    "torque_max":       200.0,
}

ARM_IDS = ["ARM-001", "ARM-002", "ARM-003", "ARM-004", "ARM-005"]
JOINTS  = ["shoulder", "elbow", "wrist"]

WEAR_LABELS     = ["Normal", "Warning", "Failure"]
STATUS_LABELS   = ["normal", "warning", "failure"]
INTEGRITY_LABELS= ["ok", "suspicious", "compromised"]

# ML feature columns (no leakage from derived targets)
ML_FEATURES = ["temperature", "pressure", "vibration", "rpm", "current", "torque"]
ML_TARGET   = "wear_label"

APP_VERSION = "1.0.0"
