"""Tests for ML training, persistence, and prediction."""
import pytest
import os
from app.services.dataset_generator import generate
from app.services.ml_service import train, predict, is_model_available, get_metrics
from app.utils.config import WEAR_LABELS


@pytest.fixture(scope="module")
def trained_model():
    df = generate(n_rows=600)
    metrics = train(df)
    return metrics


def test_training_produces_metrics(trained_model):
    m = trained_model
    assert "accuracy" in m
    assert 0.0 <= m["accuracy"] <= 1.0
    assert "confusion_matrix" in m
    assert "feature_importance" in m


def test_metrics_have_all_classes(trained_model):
    per_class = trained_model["per_class"]
    for cls in WEAR_LABELS:
        assert cls in per_class, f"Missing class in per_class metrics: {cls}"


def test_model_available_after_training(trained_model):
    assert is_model_available()


def test_prediction_returns_valid_class():
    result = predict({
        "temperature": 55.0, "pressure": 4.5, "vibration": 1.5,
        "rpm": 1800.0, "current": 7.0, "torque": 40.0
    })
    assert result["predicted_class"] in WEAR_LABELS
    assert sum(result["probabilities"].values()) == pytest.approx(1.0, abs=0.01)


def test_prediction_failure_reading():
    result = predict({
        "temperature": 95.0, "pressure": 9.0, "vibration": 7.5,
        "rpm": 3300.0, "current": 15.5, "torque": 112.0
    })
    assert result["predicted_class"] in WEAR_LABELS


def test_predict_missing_feature_raises():
    with pytest.raises(ValueError):
        predict({"temperature": 55.0})  # missing other features
