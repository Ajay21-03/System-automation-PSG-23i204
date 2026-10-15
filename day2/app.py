"""
DAY 2 ┬╖ ML-Based Industrial Predictive Maintenance Dashboard
23IF02 System Automation ΓÇö PSG Tech

Flask Application & Decision Engine:
- Sensor Data -> ML Prediction -> Decision -> Action -> Logging
- Local Web Dashboard displaying status, telemetry, metrics, and alerts.
"""

import csv
from datetime import datetime
from pathlib import Path
import random
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from flask import Flask, flash, jsonify, redirect, render_template, request
import joblib
import pandas as pd

# Paths strictly within day2/
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "day2_sample.csv"
MODEL_PATH = BASE_DIR / "predictive_maintenance_model.joblib"
ALERTS_PATH = BASE_DIR / "alerts.csv"
LOG_PATH = BASE_DIR / "system.log"

app = Flask(__name__)
app.secret_key = "system-automation-psg-23i204-secret"

# Global in-memory state for latest reading
latest_state = {
    "temperature": 64.20,
    "pressure": 5.10,
    "vibration": 2.10,
    "current": 11.80,
    "rpm": 1820,
    "status": "NORMAL",
    "severity": "Normal",
    "confidence": 98.0,
    "probabilities": {"NORMAL": 0.98},
    "action": "Routine operational log maintained. System functioning within normal tolerances.",
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}

# ---------------------------------------------------------------------------
# LOGGING HELPER
# ---------------------------------------------------------------------------
def log_system_event(level: str, message: str):
    """Append a timestamped system event message to day2/system.log."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} [{level}] {message}\n")
    except Exception as e:
        print(f"[!] Logging error: {e}")


# ---------------------------------------------------------------------------
# MODEL LOADER
# ---------------------------------------------------------------------------
def load_trained_model():
    """Load the model pipeline and metadata from the joblib artifact."""
    if not MODEL_PATH.exists():
        log_system_event("ERROR", f"Model file not found at {MODEL_PATH}")
        return None, None, None, {}
    try:
        artifact = joblib.load(MODEL_PATH)
        return (
            artifact["pipeline"],
            artifact["feature_names"],
            artifact["classes"],
            artifact.get("metrics", {}),
        )
    except Exception as e:
        log_system_event("ERROR", f"Failed loading model artifact: {e}")
        return None, None, None, {}


# ---------------------------------------------------------------------------
# 3. DECISION ENGINE
# ---------------------------------------------------------------------------
def predict_status(sensor_data: dict) -> tuple[str, float, dict]:
    """Predict machine status using the trained Random Forest pipeline."""
    pipeline, feature_names, classes, _ = load_trained_model()
    if pipeline is None:
        raise RuntimeError("Model pipeline is not loaded.")

    # Form a 1-row DataFrame with the exact feature order
    row_df = pd.DataFrame([[sensor_data[f] for f in feature_names]], columns=feature_names)

    # Prediction & probability
    predicted_class = str(pipeline.predict(row_df)[0])
    probabilities = pipeline.predict_proba(row_df)[0]
    prob_dict = {cls: round(float(p) * 100, 1) for cls, p in zip(classes, probabilities)}
    confidence = prob_dict.get(predicted_class, 0.0)

    return predicted_class, confidence, prob_dict


def make_decision(status: str) -> dict:
    """Evaluate predicted condition and map to machine status severity & recommended action."""
    # Mapping to standard three-tier status (Normal / Warning / Failure)
    if status == "NORMAL":
        return {
            "severity": "Normal",
            "title": "Nominal Operation",
            "action": "Routine operational log maintained. All telemetry parameters within safe design limits.",
            "recommendation": "Continue scheduled manufacturing batch. Log continuous telemetry.",
        }
    elif status == "LOW_PRESSURE":
        return {
            "severity": "Warning",
            "title": "Pneumatic / Hydraulic Pressure Warning",
            "action": "Inspection Warning: Pressure dropped below 4.0 bar. Inspect supply lines, compressor, and check-valves.",
            "recommendation": "Check for pneumatic seal leakage and verify line accumulator pressure.",
        }
    elif status == "MOTOR_OVERLOAD":
        return {
            "severity": "Warning",
            "title": "Motor Overcurrent / Overload Warning",
            "action": "Inspection Warning: Current draw exceeded 16.0 A. Check motor mechanical load and winding insulation.",
            "recommendation": "Verify driven mechanism for jamming or bearing friction. Throttle feed rate.",
        }
    elif status == "OVERHEATING":
        return {
            "severity": "Failure",
            "title": "Critical Thermal Overheating Alert",
            "action": "CRITICAL ALERT: Machine temperature exceeded 70┬░C threshold. Schedule thermal stabilization.",
            "recommendation": "Inspect cooling fluid circulation, coolant fins, and mechanical bearing lubrication.",
        }
    elif status == "HIGH_VIBRATION":
        return {
            "severity": "Failure",
            "title": "Critical Mechanical Vibration Alert",
            "action": "CRITICAL ALERT: Excessive vibration (> 3.5 mm/s) detected. High risk of bearing or shaft damage.",
            "recommendation": "Inspect shaft alignment, dynamic unbalance, and mounting bolt tightness immediately.",
        }
    else:
        return {
            "severity": "Warning",
            "title": f"Unrecognized Condition: {status}",
            "action": f"Caution: Anomalous condition detected ({status}). Technical assessment recommended.",
            "recommendation": "Perform manual inspection of mechanical equipment.",
        }


# ---------------------------------------------------------------------------
# 4. ACTION ENGINE & LOGGING
# ---------------------------------------------------------------------------
def take_action(sensor_data: dict, status: str, decision: dict):
    """Execute simulated action and append audit event to day2/alerts.csv."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Record alert row
    row = [
        timestamp,
        f"{sensor_data['temperature']:.2f}",
        f"{sensor_data['pressure']:.2f}",
        f"{sensor_data['vibration']:.2f}",
        f"{sensor_data['current']:.2f}",
        str(int(sensor_data["rpm"])),
        status,
        decision["severity"],
        decision["action"],
    ]

    try:
        file_exists = ALERTS_PATH.exists()
        with open(ALERTS_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "timestamp", "temperature", "pressure", "vibration",
                    "current", "rpm", "status", "severity", "action_taken"
                ])
            writer.writerow(row)
        log_system_event(
            "INFO",
            f"Action Taken [{decision['severity']}]: Status={status} | Temp={sensor_data['temperature']} | Action={decision['action'][:40]}..."
        )
    except Exception as e:
        log_system_event("ERROR", f"Failed to record alert in alerts.csv: {e}")


# ---------------------------------------------------------------------------
# 6. SECURITY VALIDATION
# ---------------------------------------------------------------------------
def validate_sensor_inputs(form_data: dict) -> tuple[dict | None, str | None]:
    """Validate user sensor telemetry inputs for physical feasibility and type correctness."""
    required_fields = ["temperature", "pressure", "vibration", "current", "rpm"]

    # 1. Check all required fields present
    for field in required_fields:
        if field not in form_data or str(form_data[field]).strip() == "":
            err = f"Missing required sensor input: '{field}'."
            log_system_event("WARNING", f"Validation Rejected: {err}")
            return None, err

    # 2. Check numeric conversion
    try:
        temp = float(form_data["temperature"])
        pres = float(form_data["pressure"])
        vib = float(form_data["vibration"])
        curr = float(form_data["current"])
        rpm = int(float(form_data["rpm"]))
    except (ValueError, TypeError) as e:
        err = f"Non-numeric sensor reading supplied: {e}. All inputs must be valid numbers."
        log_system_event("WARNING", f"Validation Rejected: {err}")
        return None, err

    # 3. Check physical constraints (non-negative and plausible demonstration limits)
    if temp < 0.0 or temp > 200.0:
        err = f"Temperature ({temp}┬░C) outside demonstration safety range (0.0 to 200.0┬░C)."
        log_system_event("WARNING", f"Validation Rejected: {err}")
        return None, err

    if pres < 0.0 or pres > 20.0:
        err = f"Pressure ({pres} bar) cannot be negative or exceed demonstration maximum (0.0 to 20.0 bar)."
        log_system_event("WARNING", f"Validation Rejected: {err}")
        return None, err

    if vib < 0.0 or vib > 30.0:
        err = f"Vibration ({vib} mm/s) cannot be negative or exceed demonstration maximum (0.0 to 30.0 mm/s)."
        log_system_event("WARNING", f"Validation Rejected: {err}")
        return None, err

    if curr < 0.0 or curr > 60.0:
        err = f"Current ({curr} A) cannot be negative or exceed demonstration maximum (0.0 to 60.0 A)."
        log_system_event("WARNING", f"Validation Rejected: {err}")
        return None, err

    if rpm < 0 or rpm > 5000:
        err = f"RPM ({rpm}) cannot be negative or exceed demonstration maximum (0 to 5000 RPM)."
        log_system_event("WARNING", f"Validation Rejected: {err}")
        return None, err

    clean = {
        "temperature": temp,
        "pressure": pres,
        "vibration": vib,
        "current": curr,
        "rpm": rpm,
    }
    return clean, None


# ---------------------------------------------------------------------------
# HELPERS FOR DASHBOARD RENDERING
# ---------------------------------------------------------------------------
def get_recent_alerts(limit: int = 10) -> list[dict]:
    """Read the latest alerts from day2/alerts.csv."""
    alerts = []
    if not ALERTS_PATH.exists():
        return alerts
    try:
        with open(ALERTS_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                alerts.append(row)
        return list(reversed(alerts))[:limit]
    except Exception as e:
        log_system_event("ERROR", f"Error reading alerts.csv: {e}")
        return []


def get_dataset_preview(limit: int = 8) -> list[dict]:
    """Read top records from day2/data/day2_sample.csv for preview."""
    if not DATA_PATH.exists():
        return []
    try:
        records = []
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= limit:
                    break
                records.append(row)
        return records
    except Exception as e:
        log_system_event("ERROR", f"Error reading day2_sample.csv: {e}")
        return []


# ---------------------------------------------------------------------------
# FLASK WEB ROUTES
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    """Main dashboard page."""
    _, _, _, metrics = load_trained_model()
    alerts = get_recent_alerts(limit=10)
    dataset_samples = get_dataset_preview(limit=8)

    return render_template(
        "index.html",
        latest=latest_state,
        metrics=metrics,
        alerts=alerts,
        dataset_samples=dataset_samples,
    )


@app.route("/predict", methods=["POST"])
def predict():
    """Process a sensor record submission (Form or JSON)."""
    # Accept Form data or JSON payload
    data = request.json if request.is_json else request.form.to_dict()

    clean_data, error_msg = validate_sensor_inputs(data)
    if error_msg:
        if request.is_json:
            return jsonify({"success": False, "error": error_msg}), 400
        flash(f"Input Validation Error: {error_msg}", "danger")
        return redirect("/")

    try:
        # 1. SENSOR DATA -> 2. ML PREDICTION -> 3. DECISION -> 4. ACTION -> 5. LOGGING
        status, confidence, prob_dict = predict_status(clean_data)
        decision = make_decision(status)
        take_action(clean_data, status, decision)

        # Update global memory state
        latest_state.update({
            **clean_data,
            "status": status,
            "severity": decision["severity"],
            "confidence": confidence,
            "probabilities": prob_dict,
            "action": decision["action"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        if request.is_json:
            return jsonify({
                "success": True,
                "status": status,
                "severity": decision["severity"],
                "confidence": confidence,
                "probabilities": prob_dict,
                "action": decision["action"],
            })

        flash(
            f"Successfully processed readings: {status} ({decision['severity']}) with {confidence:.1f}% confidence.",
            "success" if decision["severity"] == "Normal" else "warning"
        )
        return redirect("/")

    except Exception as e:
        err_msg = f"Inference pipeline execution error: {e}"
        log_system_event("ERROR", err_msg)
        if request.is_json:
            return jsonify({"success": False, "error": err_msg}), 500
        flash(err_msg, "danger")
        return redirect("/")


@app.route("/test-sample", methods=["POST"])
def test_random_sample():
    """Pick a random record from the existing dataset and run the pipeline."""
    if not DATA_PATH.exists():
        flash("Dataset day2_sample.csv not found.", "danger")
        return redirect("/")

    try:
        df = pd.read_csv(DATA_PATH)
        random_row = df.sample(n=1, random_state=None).iloc[0].to_dict()

        sensor_data = {
            "temperature": float(random_row["temperature"]),
            "pressure": float(random_row["pressure"]),
            "vibration": float(random_row["vibration"]),
            "current": float(random_row["current"]),
            "rpm": int(random_row["rpm"]),
        }

        # Run pipeline
        status, confidence, prob_dict = predict_status(sensor_data)
        decision = make_decision(status)
        take_action(sensor_data, status, decision)

        latest_state.update({
            **sensor_data,
            "status": status,
            "severity": decision["severity"],
            "confidence": confidence,
            "probabilities": prob_dict,
            "action": decision["action"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        flash(
            f"Loaded Dataset Sample: Diagnosed as {status} [{decision['severity']}] (True Label: {random_row.get('state', 'N/A')})",
            "info"
        )
        return redirect("/")
    except Exception as e:
        flash(f"Error testing sample: {e}", "danger")
        return redirect("/")


@app.route("/clear-alerts", methods=["POST"])
def clear_alerts():
    """Clear alert history in alerts.csv."""
    try:
        with open(ALERTS_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "temperature", "pressure", "vibration",
                "current", "rpm", "status", "severity", "action_taken"
            ])
        log_system_event("INFO", "Alert history cleared by user.")
        flash("Alert history cleared successfully.", "info")
    except Exception as e:
        flash(f"Failed clearing alerts: {e}", "danger")
    return redirect("/")


@app.route("/api/status", methods=["GET"])
def api_status():
    """API endpoint returning latest machine status and metrics."""
    _, _, _, metrics = load_trained_model()
    return jsonify({
        "latest": latest_state,
        "metrics": metrics,
    })


if __name__ == "__main__":
    log_system_event("INFO", "Starting Flask Industrial Maintenance Dashboard on http://127.0.0.1:5000")
    print("\n" + "=" * 65)
    print("  INDUSTRIAL PREDICTIVE MAINTENANCE DASHBOARD ΓÇö DAY 2")
    print("  Access web interface at: http://127.0.0.1:5000")
    print("=" * 65 + "\n")
    # Development mode only for local college demonstration
    app.run(host="127.0.0.1", port=5000, debug=True)
