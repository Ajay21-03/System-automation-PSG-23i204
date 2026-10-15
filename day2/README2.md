# 23IF02 System Automation ΓÇö Industrial Predictive Maintenance System

Welcome to the **System Automation (23IF02)** laboratory project at **PSG College of Technology**.

This repository contains an end-to-end implementation of an **ML-Based Industrial Predictive Maintenance System (Day 2)**. It continuously monitors multivariate sensor telemetry from industrial machinery, classifies machine health, makes automated operational decisions, executes safe simulated actions, logs audit trails, and provides a real-time web dashboard.

---

## Complete Project Architecture & Operational Flow

The Day 2 system follows a 6-stage closed-loop automation workflow:

```text
ΓöîΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÉ      ΓöîΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÉ      ΓöîΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÉ
Γöé  1. SENSOR TELEMETRY   Γöé ΓöÇΓöÇΓöÇΓû║ Γöé  2. SECURITY VALIDATION   Γöé ΓöÇΓöÇΓöÇΓû║ Γöé   3. ML PREDICTION      Γöé
Γöé  day2/data/            Γöé      Γöé  app.py                   Γöé      Γöé   train_model.py        Γöé
Γöé  day2_sample.csv       Γöé      Γöé  validate_sensor_inputs() Γöé      Γöé   predict_status()      Γöé
ΓööΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÿ      ΓööΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÿ      ΓööΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÿ
                                                                                 Γöé
                                                                                 Γû╝
ΓöîΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÉ      ΓöîΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÉ      ΓöîΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÉ
Γöé  6. FLASK WEB HMI      Γöé ΓùäΓöÇΓöÇΓöÇ Γöé  5. ACTION ENGINE & LOG   Γöé ΓùäΓöÇΓöÇΓöÇ Γöé   4. DECISION ENGINE    Γöé
Γöé  templates/index.html  Γöé      Γöé  alerts.csv / system.log  Γöé      Γöé   app.py                Γöé
Γöé  static/style.css      Γöé      Γöé  take_action()            Γöé      Γöé   make_decision()       Γöé
ΓööΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÿ      ΓööΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÿ      ΓööΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÿ
```

---

## Detailed Step-by-Step Flow for Mentor Presentation

When explaining this project to your mentor or evaluators, walk through these **6 chronological stages**:

### Stage 1: Data Telemetry & Sensor Signal Acquisition
- **Primary Files:**
  - [`day2/data/day2_sample.csv`](day2/data/day2_sample.csv): 250 time-indexed sensor records representing real machine telemetry.
  - [`day2/data/day2_sample.py`](day2/data/day2_sample.py) / [`day2/generate_sensor_data.py`](day2/generate_sensor_data.py): Industrial data generator.
- **Monitored Features:**
  - `temperature` (┬░C): Nominal range 55.0 ΓÇô 70.0 ┬░C.
  - `pressure` (bar): Nominal range 4.0 ΓÇô 6.5 bar.
  - `vibration` (mm/s): Nominal range 1.0 ΓÇô 3.5 mm/s.
  - `current` (A): Nominal range 8.0 ΓÇô 16.0 A.
  - `rpm` (RPM): Nominal range 1400 ΓÇô 2200 RPM.
- **Main Functions:**
  - `generate_sensor_data(tick)`: Generates realistic multivariate sensor telemetry with injected anomalies matching factory proportions.
  - `get_machine_status(temp, pres, vib, curr, rpm)`: Applies physical threshold logic to assign ground-truth machine states (`NORMAL`, `OVERHEATING`, `LOW_PRESSURE`, `HIGH_VIBRATION`, `MOTOR_OVERLOAD`).
  - `save_to_csv(records, filename)`: Formats and exports data to CSV.

---

### Stage 2: Machine Learning Model Training & Evaluation
- **Primary Files:**
  - [`day2/train_model.py`](day2/train_model.py): Model training and evaluation script.
  - [`day2/predictive_maintenance_model.joblib`](day2/predictive_maintenance_model.joblib): Serialized model pipeline bundle.
  - [`day2/results/`](day2/results/): Visual artifacts (`confusion_matrix.png`, `feature_importance.png`, `evaluation_report.txt`).
- **Algorithm:** **Random Forest Classifier** wrapped in a leak-free scikit-learn `Pipeline`:
  $$\text{Raw Telemetry} \longrightarrow \text{SimpleImputer (Median)} \longrightarrow \text{StandardScaler} \longrightarrow \text{RandomForestClassifier (200 trees, balanced weights)}$$
- **Main Functions in `train_model.py`:**
  - `inspect_dataset(df)`: Conducts exploratory data analysis (EDA), checking null counts, data types, and class balance.
  - `train_and_evaluate()`:
    1. Splits data using `train_test_split(..., test_size=0.20, stratify=y, random_state=42)` (200 train / 50 test).
    2. Runs 5-Fold Stratified Cross-Validation strictly on the training partition (`Mean CV Accuracy: 99.0%`, `Macro F1: 0.9794`).
    3. Fits the Random Forest pipeline on training data with `class_weight='balanced'` to prevent bias toward the majority `NORMAL` class.
    4. Evaluates on the held-out 50-sample test set:
       - **Test Accuracy:** **100.0%**
       - **Macro F1-Score:** **1.0000**
       - **Failure Recall:** **100.0%** (Zero missed machine breakdowns).
    5. Calculates Gini feature importance: `current` (25.1%), `temperature` (24.3%), `pressure` (24.0%), `vibration` (23.5%), `rpm` (3.1%).
    6. Saves plots and exports the fitted pipeline bundle with metadata to `predictive_maintenance_model.joblib`.

---

### Stage 3: Security & Input Validation Layer
- **Primary Files:**
  - [`day2/app.py`](day2/app.py): Server-side validation logic.
  - [`day2/system.log`](day2/system.log): Audit trail of rejected inputs and server events.
- **Purpose:** Protects the ML inference engine against garbage, corrupted, or non-physical data before it touches the model.
- **Main Functions in `app.py`:**
  - `validate_sensor_inputs(form_data)`:
    - **Completeness:** Ensures all 5 sensor fields exist.
    - **Data Types:** Rejects non-numeric strings or invalid numbers.
    - **Non-Negativity Checks:** Flags physically impossible values like negative pressure or negative vibration.
    - **Physical Bounds:** Validates values within demonstration ranges (e.g., Temp 0ΓÇô200┬░C, Pressure 0ΓÇô20 bar, Current 0ΓÇô60 A).
  - `log_system_event(level, message)`: Writes timestamped rejection warnings and errors to `system.log`.

---

### Stage 4: Decision Engine (ML Inference & Diagnosis)
- **Primary Files:**
  - [`day2/app.py`](day2/app.py): Web server decision engine.
  - [`day2/predict_machine.py`](day2/predict_machine.py): Standalone terminal diagnostic CLI.
- **Purpose:** Uses the trained ML model to diagnose machine health and decide operational severity.
- **Main Functions in `app.py`:**
  - `load_trained_model()`: Loads the pipeline, feature names, and metadata from `predictive_maintenance_model.joblib`.
  - `predict_status(sensor_data)`: Feeds validated readings through the pipeline, returning predicted condition (`NORMAL`, `OVERHEATING`, `LOW_PRESSURE`, `HIGH_VIBRATION`, `MOTOR_OVERLOAD`), confidence percentage, and per-class probability distribution.
  - `make_decision(status)`: Maps condition to operational severity tiers and maintenance protocols:
    - `NORMAL` $\to$ **Normal:** Continue routine monitoring; no intervention required.
    - `LOW_PRESSURE` $\to$ **Warning:** Pneumatic/hydraulic line pressure drop; inspect compressor, seals, and check-valves.
    - `MOTOR_OVERLOAD` $\to$ **Warning:** Motor overcurrent draw; inspect mechanical jamming, bearing friction, and VFD.
    - `OVERHEATING` $\to$ **Failure:** Thermal runaway (>70┬░C); trigger critical alert, throttle motor, inspect cooling system.
    - `HIGH_VIBRATION` $\to$ **Failure:** Mechanical imbalance (>3.5 mm/s); trigger critical alert, inspect shaft alignment and bearing race.

---

### Stage 5: Action Engine & Audit Logging
- **Primary Files:**
  - [`day2/app.py`](day2/app.py): Action dispatch function.
  - [`day2/alerts.csv`](day2/alerts.csv): Persistent CSV ledger.
- **Purpose:** Executes safe simulated responses and logs every decision for regulatory and quality audits.
- **Main Function in `app.py`:**
  - `take_action(sensor_data, status, decision)`:
    - Simulates safe physical actions (logging, operator alert, urgent inspection advisory) without dangerous physical machinery shutdowns.
    - Appends event to `day2/alerts.csv`:
      `timestamp`, `temperature`, `pressure`, `vibration`, `current`, `rpm`, `status`, `severity`, `action_taken`.
    - Logs execution in `day2/system.log`.

---

### Stage 6: Human-Machine Interface (Flask Web Dashboard)
- **Primary Files:**
  - [`day2/app.py`](day2/app.py): Backend routes.
  - [`day2/templates/index.html`](day2/templates/index.html): HTML5 Jinja2 template.
  - [`day2/static/style.css`](day2/static/style.css): Industrial dark-theme CSS.
- **Main Web Routes:**
  - `index()` (`GET /`): Renders machine health status card, live telemetry gauges, model evaluation metrics, and recent alert history.
  - `predict()` (`POST /predict`): Receives manual telemetry from the web form, runs Validation $\to$ ML Prediction $\to$ Decision Engine $\to$ Action Engine $\to$ Alert Log, and updates the UI.
  - `test_random_sample()` (`POST /test-sample`): Picks a random historical record from `day2_sample.csv` to demonstrate model diagnosis against ground truth.
  - `clear_alerts()` (`POST /clear-alerts`): Resets the `alerts.csv` log table.
  - `api_status()` (`GET /api/status`): JSON REST endpoint for integration with external SCADA / PLC automation systems.
- **Interactive UI Features:**
  - **Quick Preset Buttons:** One-click simulation for *Normal*, *Overheating*, *Low Pressure*, *High Vibration*, and *Motor Overload*.
  - **Telemetry Cards:** Instant visual readout of Temperature, Pressure, Vibration, Current, and RPM with safe operating limits.
  - **Real-time Metrics:** Displays Accuracy, 5-Fold Cross-Val score, Macro F1, Failure Recall (100%), and Gini Feature Importance bars.

---

## File Summary Quick-Reference Table

| File Path | Role in System | Key Functions / Elements | Output Artifact / Impact |
| :--- | :--- | :--- | :--- |
| [`day2/data/day2_sample.csv`](day2/data/day2_sample.csv) | Telemetry Dataset | 250 rows $\times$ 6 columns | Ground truth dataset for ML |
| [`day2/data/day2_sample.py`](day2/data/day2_sample.py) | Data Generator | `generate_sensor_data()`, `get_machine_status()` | Populates CSV with sensor data |
| [`day2/train_model.py`](day2/train_model.py) | Model Training & Evaluation | `inspect_dataset()`, `train_and_evaluate()` | Generates `predictive_maintenance_model.joblib` |
| [`day2/app.py`](day2/app.py) | Decision & Action Server | `validate_sensor_inputs()`, `predict_status()`, `make_decision()`, `take_action()` | Runs Flask web dashboard on `http://127.0.0.1:5000` |
| [`day2/predict_machine.py`](day2/predict_machine.py) | Terminal Diagnostic CLI | `load_model()`, `validate_readings()`, `detect_status()` | Command-line inference & demos |
| [`day2/alerts.csv`](day2/alerts.csv) | Audit Ledger | CSV log records | Immutable history of alerts and actions |
| [`day2/system.log`](day2/system.log) | System & Security Log | Timestamped event stream | Records rejected inputs & errors |
| [`day2/templates/index.html`](day2/templates/index.html) | Dashboard UI | Jinja2 templates, SVG icons, Presets | Interactive web interface |
| [`day2/static/style.css`](day2/static/style.css) | UI Design System | CSS variables, responsive grid, glassmorphism | Professional industrial aesthetic |
| [`day2/requirements.txt`](day2/requirements.txt) | Dependencies | `pandas`, `scikit-learn`, `flask`, `joblib`, `matplotlib` | Reproducible environment setup |

---

## How to Run the Demonstration

```powershell
# 1. Open terminal and navigate into day2
cd day2

# 2. Install dependencies
python -m pip install -r requirements.txt

# 3. Train the Random Forest ML model
python train_model.py

# 4. Launch the Web Dashboard
python app.py
```

Open your browser at:
```text
http://127.0.0.1:5000
```

---

## Key Talking Points for Your Mentor

1. **Why Random Forest?** Handles non-linear multi-sensor relationships, robust against overfitting, provides interpretable Gini feature importances, and excels on tabular sensor telemetry.
2. **Why Failure Recall Matters Most:** In predictive maintenance, missing a catastrophic breakdown (`False Negative`) causes factory shutdowns and dangerous equipment failure. Achieving **100% Failure Recall** ensures zero missed failures.
3. **Closed-Loop Automation:** The system is not just an ML classifier; it includes a **Decision Engine** (severity classification), an **Action Engine** (prescribed protocols), **Audit Logging** (`alerts.csv`), and a **Security Validation Layer** (`system.log`).
4. **Known Scientific Limitation:** Because dataset labels were originally synthesized using physical thresholds (e.g. Temp > 70┬░C), the model learns optimal boundary approximations for anomaly detection. True future-forecasting prognostic maintenance would require run-to-failure historical logs with Remaining Useful Life (RUL) tracking.
