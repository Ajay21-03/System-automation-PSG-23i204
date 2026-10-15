"""Rule engine / automation rules endpoint."""
from flask import Blueprint
from app.utils.response import ok
from app.services.rule_engine import get_rules_with_stats, RULES
from app.utils.config import THRESHOLDS

bp = Blueprint("automation", __name__)


@bp.get("/api/automation/rules")
def rules():
    return ok({
        "rules":      get_rules_with_stats(),
        "thresholds": THRESHOLDS,
        "workflow": {
            "steps": ["Sense", "Think", "Act", "Log"],
            "description": (
                "SENSE: Raw sensor values are read from the dataset or API input. "
                "THINK: Rule engine evaluates each reading against configured thresholds. "
                "ACT: The decision engine applies priority logic and emits a decision. "
                "LOG: All triggered rules and decisions are written to the audit log."
            ),
        },
        "disclaimer": (
            "All threshold values are simulation assumptions for academic purposes. "
            "They are NOT certified industrial safety limits."
        ),
    })
