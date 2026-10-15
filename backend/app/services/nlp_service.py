"""
Maintenance log NLP service.
Keyword-based analysis with basic negation handling.

DISCLAIMER: This is rule-based keyword matching, NOT a trained NLP model.
Results are indicative only and must not substitute for a qualified
technician's diagnosis.
"""
import re
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Keyword categories with severity weights
KEYWORD_GROUPS = {
    "vibration":    {"keywords": ["vibrat", "shake", "shak", "trembl"], "severity": "warning"},
    "grinding":     {"keywords": ["grind", "scrape", "grat", "squeal"], "severity": "critical"},
    "overheating":  {"keywords": ["overheat", "hot", "burn", "thermal", "heat"], "severity": "critical"},
    "torque":       {"keywords": ["torque", "torq", "twist", "torsion"], "severity": "warning"},
    "loose":        {"keywords": ["loose", "slack", "play", "wobbl"], "severity": "warning"},
    "noise":        {"keywords": ["noise", "sound", "loud", "clank", "bang", "rattle"], "severity": "warning"},
    "leak":         {"keywords": ["leak", "drip", "seep", "fluid"], "severity": "critical"},
    "wear":         {"keywords": ["wear", "worn", "degrad", "deteriorat"], "severity": "warning"},
    "normal":       {"keywords": ["normal", "fine", "ok", "good", "clean", "routine", "scheduled", "inspection", "check"], "severity": "info"},
    "maintenance":  {"keywords": ["replac", "lubricate", "lubricat", "oil", "grease", "calibrat", "adjust", "tighten"], "severity": "info"},
    "failure":      {"keywords": ["fail", "broke", "broken", "fault", "error", "alarm", "trip", "stop"], "severity": "critical"},
}

# Negation words — if these precede a keyword within 3 tokens, the hit is negated
NEGATION_WORDS = {"no", "not", "without", "none", "never", "absence", "absent", "nor",
                  "didn't", "did not", "wasn't", "was not", "isn't", "is not"}

# ARM and JOINT detection patterns
ARM_PATTERN   = re.compile(r"\barm[-\s]?(\d+|[A-Z]\d{3})\b", re.IGNORECASE)
JOINT_PATTERN = re.compile(r"\b(shoulder|elbow|wrist)\b", re.IGNORECASE)


def _tokenize(text: str) -> list:
    return re.split(r"\W+", text.lower())


def _check_negated(tokens: list, keyword_idx: int, window: int = 3) -> bool:
    start = max(0, keyword_idx - window)
    context = tokens[start:keyword_idx]
    for neg in NEGATION_WORDS:
        for word in neg.split():
            if word in context:
                return True
    return False


def analyze_note(text: str) -> dict:
    """Analyze a single maintenance note. Returns structured result."""
    tokens = _tokenize(text)
    detected_groups   = []
    negated_groups    = []
    highest_severity  = "info"

    severity_rank = {"info": 0, "warning": 1, "critical": 2}

    for group_name, group_data in KEYWORD_GROUPS.items():
        for kw in group_data["keywords"]:
            for i, token in enumerate(tokens):
                if kw in token:
                    if _check_negated(tokens, i):
                        if group_name not in negated_groups:
                            negated_groups.append(group_name)
                    else:
                        if group_name not in detected_groups:
                            detected_groups.append(group_name)
                            sev = group_data["severity"]
                            if severity_rank.get(sev, 0) > severity_rank.get(highest_severity, 0):
                                highest_severity = sev
                    break

    # Detect arm and joint
    arm_match   = ARM_PATTERN.search(text)
    joint_match = JOINT_PATTERN.search(text)
    arm_id      = arm_match.group(0).upper().replace(" ", "-") if arm_match else None
    joint       = joint_match.group(1).lower() if joint_match else None

    # Relevance classification
    action_groups = {"vibration", "grinding", "overheating", "torque",
                     "loose", "noise", "leak", "wear", "failure"}
    relevant = bool(set(detected_groups) & action_groups)

    # Build explanation
    explanation_parts = []
    if detected_groups:
        explanation_parts.append(f"Detected indicators: {', '.join(detected_groups)}.")
    if negated_groups:
        explanation_parts.append(f"Negated (not triggered): {', '.join(negated_groups)}.")
    if not relevant:
        explanation_parts.append("Note appears to be administrative or routine in nature.")
    else:
        explanation_parts.append(
            "Keyword analysis suggests the note may indicate a maintenance concern. "
            "This is NOT a definitive diagnosis — a qualified technician must inspect the equipment."
        )

    return {
        "original_text":   text,
        "arm_id":          arm_id,
        "joint":           joint,
        "detected_terms":  detected_groups,
        "negated_terms":   negated_groups,
        "severity":        highest_severity,
        "relevant":        relevant,
        "analyzed_at":     datetime.now(timezone.utc).isoformat(),
        "explanation":     " ".join(explanation_parts),
        "disclaimer":      (
            "Keyword-based analysis only. Results are indicative. "
            "Not a verified technician diagnosis."
        ),
    }


def analyze_log_file(path: str) -> list:
    """Analyze all entries in a maintenance log file (one note per line or --- separated)."""
    results = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        entries = re.split(r"\n---+\n|\n\n+", content.strip())
        for entry in entries:
            entry = entry.strip()
            if entry and not entry.startswith("#"):
                results.append(analyze_note(entry))
    except FileNotFoundError:
        logger.warning("Maintenance log not found: %s", path)
    return results
