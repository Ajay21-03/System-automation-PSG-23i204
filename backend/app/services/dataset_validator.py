"""
Dataset validator.
Checks row count, schema, labels, ranges, missing values, duplicates,
and class distribution. Returns a structured report.
"""
import os
import pandas as pd
from app.utils.config import DATASET_PATH, DATASET_ROWS, WEAR_LABELS, THRESHOLDS

REQUIRED_COLUMNS = [
    "timestamp", "arm_id", "joint",
    "temperature", "pressure", "vibration",
    "rpm", "current", "torque",
    "status", "wear_label", "failure_event", "sensor_integrity",
]

COLUMN_RANGES = {
    "temperature": (THRESHOLDS["temperature_min"], THRESHOLDS["temperature_max"]),
    "pressure":    (THRESHOLDS["pressure_min"],    THRESHOLDS["pressure_max"]),
    "vibration":   (THRESHOLDS["vibration_min"],   THRESHOLDS["vibration_max"]),
    "rpm":         (THRESHOLDS["rpm_min"],          THRESHOLDS["rpm_max"]),
    "current":     (THRESHOLDS["current_min"],      THRESHOLDS["current_max"]),
    "torque":      (THRESHOLDS["torque_min"],        THRESHOLDS["torque_max"]),
}


def validate(path: str = DATASET_PATH) -> dict:
    checks = []
    passed = True

    def check(name, ok, detail=""):
        nonlocal passed
        if not ok:
            passed = False
        checks.append({"check": name, "passed": ok, "detail": detail})

    # File exists
    if not os.path.exists(path):
        check("file_exists", False, f"Not found: {path}")
        return {"passed": False, "checks": checks, "summary": "Dataset file missing."}

    check("file_exists", True, path)

    try:
        df = pd.read_csv(path)
    except Exception as e:
        check("file_readable", False, str(e))
        return {"passed": False, "checks": checks, "summary": str(e)}

    check("file_readable", True)

    # Row count
    check("row_count", len(df) == DATASET_ROWS,
          f"Expected {DATASET_ROWS}, found {len(df)}")

    # Schema
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    check("schema_complete", len(missing_cols) == 0,
          f"Missing columns: {missing_cols}" if missing_cols else "All columns present")

    # Missing values
    null_counts = df.isnull().sum()
    total_nulls = int(null_counts.sum())
    check("no_missing_values", total_nulls == 0,
          f"Total nulls: {total_nulls} | Per column: {null_counts[null_counts > 0].to_dict()}")

    # Duplicate rows
    dup_count = int(df.duplicated().sum())
    check("no_duplicate_rows", dup_count == 0, f"Duplicates found: {dup_count}")

    # Valid wear_labels
    if "wear_label" in df.columns:
        invalid_labels = df[~df["wear_label"].isin(WEAR_LABELS)]
        check("valid_wear_labels", len(invalid_labels) == 0,
              f"Invalid labels: {invalid_labels['wear_label'].unique().tolist()}" if len(invalid_labels) else "All valid")

    # Feature ranges
    for col, (lo, hi) in COLUMN_RANGES.items():
        if col in df.columns:
            out_of_range = ((df[col] < lo) | (df[col] > hi)).sum()
            check(f"range_{col}", int(out_of_range) == 0,
                  f"{out_of_range} values outside [{lo}, {hi}]")

    # Class distribution
    if "wear_label" in df.columns:
        dist = df["wear_label"].value_counts().to_dict()
        check("class_distribution_present",
              all(lbl in dist for lbl in WEAR_LABELS),
              str(dist))

    # Leakage guard: failure_event must not be in ML features
    ml_feat_cols = ["temperature", "pressure", "vibration", "rpm", "current", "torque"]
    leakage_risk = "failure_event" in ml_feat_cols
    check("no_feature_leakage", not leakage_risk,
          "failure_event column is NOT in ML features — OK")

    dist = df["wear_label"].value_counts().to_dict() if "wear_label" in df.columns else {}

    return {
        "passed": passed,
        "checks": checks,
        "rows":   len(df),
        "class_distribution": dist,
        "columns": list(df.columns),
        "summary": "All checks passed." if passed else "One or more checks failed.",
    }
