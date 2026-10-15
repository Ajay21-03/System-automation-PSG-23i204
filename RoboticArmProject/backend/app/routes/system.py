"""System status endpoint."""
import os
from flask import Blueprint
from app.utils.response import ok
from app.utils.config import (
    DATASET_PATH, MODEL_PATH, DB_PATH, APP_VERSION, THRESHOLDS
)
from app.services.ml_service import is_model_available

bp = Blueprint("system", __name__)


@bp.get("/api/system/status")
def system_status():
    return ok({
        "version":          APP_VERSION,
        "dataset_exists":   os.path.exists(DATASET_PATH),
        "model_exists":     os.path.exists(MODEL_PATH),
        "db_exists":        os.path.exists(DB_PATH),
        "model_loaded":     is_model_available(),
        "dataset_path":     DATASET_PATH,
        "model_path":       MODEL_PATH,
        "thresholds":       THRESHOLDS,
        "disclaimer": (
            "Threshold values are simulation assumptions only. "
            "Not certified industrial safety limits."
        ),
    })
