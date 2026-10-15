"""ML analytics metrics endpoint."""
from flask import Blueprint
from app.utils.response import ok, error
from app.services.ml_service import get_metrics, is_model_available

bp = Blueprint("analytics", __name__)


@bp.get("/api/analytics/metrics")
def metrics():
    m = get_metrics()
    if m is None:
        return ok({
            "model_available": False,
            "message": "Model not trained yet. Use /api/model/train to train.",
        })
    return ok({"model_available": True, **m})
