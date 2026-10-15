"""Prediction and full decision evaluation endpoints."""
from flask import Blueprint, request
from app.utils.response import ok, error
from app.services.decision_engine import evaluate as decide, demo_all_outcomes
from app.services.ml_service import predict as ml_predict, is_model_available
from app.utils.config import ML_FEATURES
from app.utils.audit import log_event

bp = Blueprint("predict", __name__)

REQUIRED = ML_FEATURES  # ["temperature","pressure","vibration","rpm","current","torque"]


def _validate_input(body: dict):
    missing = [f for f in REQUIRED if f not in body]
    if missing:
        return None, f"Missing fields: {missing}"
    vals = {}
    for f in REQUIRED:
        try:
            vals[f] = float(body[f])
        except (TypeError, ValueError):
            return None, f"Field '{f}' must be numeric"
    return vals, None


@bp.post("/api/predict")
def predict():
    body = request.get_json(silent=True) or {}
    vals, err = _validate_input(body)
    if err:
        return error(err, 422)

    if not is_model_available():
        return error("ML model is not available. Train the model first.", 503)

    try:
        result = ml_predict(vals)
    except Exception as e:
        return error(f"Prediction failed: {e}", 500)

    log_event("ml_prediction", description=f"Predicted: {result['predicted_class']}",
              evidence={"features": vals, "result": result})
    return ok(result)


@bp.post("/api/decisions/evaluate")
def evaluate_decision():
    body = request.get_json(silent=True) or {}
    vals, err = _validate_input(body)
    if err:
        return error(err, 422)

    machine_id     = str(body.get("machine_id", "MANUAL"))
    nlp_severity   = body.get("nlp_severity")  # optional
    wear_label     = body.get("wear_label")     # optional

    reading = dict(vals)
    if wear_label:
        reading["wear_label"] = wear_label

    result = decide(reading, machine_id=machine_id, nlp_severity=nlp_severity)
    log_event("decision_evaluated", machine_id=machine_id,
              severity=result["decision"].lower(),
              decision=result["decision"], evidence={"result": result})
    return ok(result)


@bp.get("/api/decisions/demo")
def demo():
    return ok(demo_all_outcomes())
