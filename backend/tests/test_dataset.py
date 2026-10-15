"""Tests for dataset generation and validation."""
import os
import pytest
from app.services.dataset_generator import generate, save_dataset
from app.services.dataset_validator import validate
from app.utils.config import DATASET_ROWS, WEAR_LABELS, ML_FEATURES


def test_generate_exact_row_count():
    df = generate(n_rows=5000)
    assert len(df) == 5000, f"Expected 5000 rows, got {len(df)}"


def test_generate_schema():
    df = generate(n_rows=100)
    required = ["timestamp", "arm_id", "joint", "temperature", "pressure",
                 "vibration", "rpm", "current", "torque", "status",
                 "wear_label", "failure_event", "sensor_integrity"]
    for col in required:
        assert col in df.columns, f"Missing column: {col}"


def test_generate_valid_labels():
    df = generate(n_rows=500)
    assert set(df["wear_label"].unique()).issubset(set(WEAR_LABELS))


def test_no_missing_values():
    df = generate(n_rows=500)
    assert df.isnull().sum().sum() == 0


def test_no_leakage_in_ml_features():
    """failure_event must not be in ML feature list."""
    assert "failure_event" not in ML_FEATURES
    assert "wear_label"    not in ML_FEATURES


def test_class_distribution_all_present():
    df = generate(n_rows=5000)
    dist = df["wear_label"].value_counts()
    for lbl in WEAR_LABELS:
        assert lbl in dist.index, f"Missing class: {lbl}"


def test_validator_passes_on_generated(tmp_path):
    df = generate(n_rows=5000)
    path = str(tmp_path / "test_data.csv")
    df.to_csv(path, index=False)
    result = validate(path)
    assert result["passed"], f"Validation failed: {result}"


def test_reproducibility():
    df1 = generate(n_rows=100, seed=42)
    df2 = generate(n_rows=100, seed=42)
    assert df1["temperature"].tolist() == df2["temperature"].tolist()
