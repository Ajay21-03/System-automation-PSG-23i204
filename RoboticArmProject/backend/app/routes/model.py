"""Model training and status endpoints."""
from flask import Blueprint, request
from app.utils.response import ok, error
from app.services.ml_service import train, get_metrics, is_model_available
from app.services.dataset_generator import load_dataset
from app.services.persistence import record_training
from app.utils.audit import log_event

bp = Blueprint("model", __name__)


@bp.post("/api/model/train")
def train_model():
    try:
        df = load_dataset()
    except FileNotFoundError:
        return error("Dataset not found. Generate it first via /api/dataset/generate", 503)

    try:
        metrics = train(df)
        record_training(metrics)
        log_event("model_trained", description=f"Accuracy={metrics['accuracy']:.4f}",
                  evidence={"accuracy": metrics["accuracy"], "macro_f1": metrics["macro_f1"]})
        return ok(metrics, "Model trained successfully")
    except Exception as e:
        return error(f"Training failed: {e}", 500)


@bp.get("/api/model/status")
def model_status():
    m = get_metrics()
    return ok({
        "model_available": is_model_available(),
        "metrics":         m,
    })
