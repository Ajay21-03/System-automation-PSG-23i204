from flask import Blueprint
from app.utils.response import ok

bp = Blueprint("health", __name__)

@bp.get("/api/health")
def health():
    return ok({"status": "running"}, "API is healthy")
