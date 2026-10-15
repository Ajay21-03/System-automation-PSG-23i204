"""
ML service — Random Forest training, persistence, and prediction.

DISCLOSURE: Trained on synthetic simulation data.
Reported metrics are for academic evaluation only.
"""
import json
import logging
import os
import numpy as np
import pandas as pd
from datetime import datetime, timezone

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, precision_recall_fscore_support
)
import joblib

from app.utils.config import (
    MODEL_PATH, METRICS_PATH, MODELS_DIR,
    ML_FEATURES, ML_TARGET, RANDOM_SEED, WEAR_LABELS
)

logger = logging.getLogger(__name__)

_model = None
_label_encoder = None
_metrics = None


def _load_model_from_disk():
    global _model, _label_encoder, _metrics
    if os.path.exists(MODEL_PATH):
        bundle = joblib.load(MODEL_PATH)
        _model         = bundle["model"]
        _label_encoder = bundle["label_encoder"]
        logger.info("ML model loaded from %s", MODEL_PATH)
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, "r") as f:
            _metrics = json.load(f)


def get_model():
    global _model
    if _model is None:
        _load_model_from_disk()
    return _model


def get_metrics() -> dict:
    global _metrics
    if _metrics is None and os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, "r") as f:
            _metrics = json.load(f)
    return _metrics


def is_model_available() -> bool:
    return get_model() is not None


def train(df: pd.DataFrame) -> dict:
    global _model, _label_encoder, _metrics
    os.makedirs(MODELS_DIR, exist_ok=True)

    # --- Validate features ---
    missing = [f for f in ML_FEATURES if f not in df.columns]
    if missing:
        raise ValueError(f"Dataset missing ML feature columns: {missing}")
    if ML_TARGET not in df.columns:
        raise ValueError(f"Dataset missing target column: {ML_TARGET}")

    X = df[ML_FEATURES].copy()
    y_raw = df[ML_TARGET].copy()

    # Encode labels
    le = LabelEncoder()
    le.fit(WEAR_LABELS)  # fixed order: Failure, Normal, Warning alphabetically → override
    le.classes_ = np.array(WEAR_LABELS)  # Normal, Warning, Failure
    y = le.transform(y_raw)

    # Stratified split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_SEED, stratify=y
    )

    # Train
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_leaf=2,
        random_state=RANDOM_SEED,
        n_jobs=-1,
        class_weight="balanced",
    )
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)

    acc = float(accuracy_score(y_test, y_pred))
    report = classification_report(y_test, y_pred,
                                   target_names=le.classes_, output_dict=True)
    cm = confusion_matrix(y_test, y_pred).tolist()

    feature_importance = {
        feat: float(imp)
        for feat, imp in zip(ML_FEATURES, clf.feature_importances_)
    }

    metrics = {
        "trained_at":          datetime.now(timezone.utc).isoformat(),
        "dataset_size":        len(df),
        "train_size":          len(X_train),
        "test_size":           len(X_test),
        "accuracy":            acc,
        "macro_precision":     report["macro avg"]["precision"],
        "macro_recall":        report["macro avg"]["recall"],
        "macro_f1":            report["macro avg"]["f1-score"],
        "weighted_precision":  report["weighted avg"]["precision"],
        "weighted_recall":     report["weighted avg"]["recall"],
        "weighted_f1":         report["weighted avg"]["f1-score"],
        "per_class":           {
            cls: {
                "precision": report[cls]["precision"],
                "recall":    report[cls]["recall"],
                "f1":        report[cls]["f1-score"],
                "support":   report[cls]["support"],
            }
            for cls in le.classes_
        },
        "confusion_matrix":    cm,
        "labels":              list(le.classes_),
        "feature_importance":  feature_importance,
        "features":            ML_FEATURES,
        "class_distribution":  {
            cls: int((y_raw == cls).sum()) for cls in WEAR_LABELS
        },
        "disclosure": (
            "Model trained on synthetic simulation data. "
            "These metrics do NOT represent real-world industrial performance."
        ),
    }

    # Persist
    joblib.dump({"model": clf, "label_encoder": le}, MODEL_PATH)
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    _model = clf
    _label_encoder = le
    _metrics = metrics

    logger.info("Model trained. Accuracy=%.4f  Path=%s", acc, MODEL_PATH)
    return metrics


def predict(features: dict) -> dict:
    """
    Predict wear class for a single reading.
    Returns predicted class, probabilities, and evidence.
    Raises RuntimeError if model is not available.
    """
    model = get_model()
    if model is None:
        raise RuntimeError("ML model is not available. Train the model first.")

    global _label_encoder
    if _label_encoder is None:
        raise RuntimeError("Label encoder not loaded.")

    row = []
    for feat in ML_FEATURES:
        val = features.get(feat)
        if val is None:
            raise ValueError(f"Missing feature value: {feat}")
        row.append(float(val))

    X = np.array(row).reshape(1, -1)
    pred_idx = model.predict(X)[0]
    proba    = model.predict_proba(X)[0]

    pred_class = _label_encoder.inverse_transform([pred_idx])[0]
    class_probs = {
        cls: float(proba[i])
        for i, cls in enumerate(_label_encoder.classes_)
    }

    return {
        "predicted_class":  pred_class,
        "probabilities":    class_probs,
        "features_used":    dict(zip(ML_FEATURES, row)),
        "predicted_at":     datetime.now(timezone.utc).isoformat(),
        "model_available":  True,
    }
