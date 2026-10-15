"""
Consistent JSON response helpers.
"""
from flask import jsonify
from datetime import datetime, timezone


def ok(data=None, message="OK", status_code=200):
    payload = {
        "success": True,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code


def error(message="An error occurred", status_code=400, details=None):
    payload = {
        "success": False,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if details is not None:
        payload["details"] = details
    return jsonify(payload), status_code
