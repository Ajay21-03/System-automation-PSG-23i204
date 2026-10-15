"""Dataset generation, validation, and info endpoints."""
import os
from flask import Blueprint, request
from app.utils.response import ok, error
from app.services.dataset_generator import generate, save_dataset, load_dataset
from app.services.dataset_validator import validate
from app.utils.config import DATASET_PATH, DATASET_ROWS
from app.utils.audit import log_event

bp = Blueprint("dataset", __name__)


@bp.get("/api/dataset/summary")
def summary():
    result = validate(DATASET_PATH)
    if not os.path.exists(DATASET_PATH):
        return ok({"available": False, "message": "Dataset not generated yet."})
    try:
        df = load_dataset()
        col_stats = {}
        for col in ["temperature","pressure","vibration","rpm","current","torque"]:
            if col in df.columns:
                col_stats[col] = {
                    "min":    round(float(df[col].min()), 2),
                    "max":    round(float(df[col].max()), 2),
                    "mean":   round(float(df[col].mean()), 2),
                    "std":    round(float(df[col].std()), 2),
                    "nulls":  int(df[col].isnull().sum()),
                }
        dist = df["wear_label"].value_counts().to_dict() if "wear_label" in df.columns else {}
        return ok({
            "available":          True,
            "rows":               len(df),
            "columns":            list(df.columns),
            "column_stats":       col_stats,
            "class_distribution": dist,
            "validation":         result,
            "path":               DATASET_PATH,
            "disclosure":         "Synthetic simulation data. Not real sensor data.",
        })
    except Exception as e:
        return error(f"Could not read dataset: {e}", 500)


@bp.post("/api/dataset/generate")
def generate_dataset():
    body = request.get_json(silent=True) or {}
    n    = int(body.get("rows", DATASET_ROWS))
    seed = int(body.get("seed", 42))

    if n < 100 or n > 50000:
        return error("rows must be between 100 and 50000", 422)

    try:
        df     = generate(n_rows=n, seed=seed)
        result = save_dataset(df)
        log_event("dataset_generated", description=f"Generated {result['rows']} rows",
                  evidence={"rows": result["rows"], "seed": seed})
        return ok(result, f"Dataset generated with {result['rows']} rows")
    except Exception as e:
        return error(f"Generation failed: {e}", 500)


@bp.get("/api/dataset/validate")
def validate_dataset():
    result = validate(DATASET_PATH)
    return ok(result)
