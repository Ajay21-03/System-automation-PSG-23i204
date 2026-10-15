# Industrial Predictive Maintenance System ΓÇö Day 2
**Course:** 23IF02 System Automation ΓÇö PSG College of Technology  
**Focus:** Supervised Machine Learning for Sensor Fault Diagnosis, Decision & Action Engine, and Web Dashboard

---

## 1. Project Objective

In industrial manufacturing, unexpected equipment downtime causes catastrophic production losses, component damage, and safety hazards. The objective of this project is to build an end-to-end automated **Industrial Predictive Maintenance System** using machine learning (**Random Forest Classifier**) that continuously monitors multivariate sensor telemetry, classifies operational machine health, decides appropriate maintenance actions, logs audit records, and provides an operator dashboard.

The system workflow follows a complete operational pipeline:
$$\text{Sensor Telemetry} \longrightarrow \text{ML Prediction} \longrightarrow \text{Decision Engine} \longrightarrow \text{Action Engine} \longrightarrow \text{Audit Logging} \longrightarrow \text{Web Dashboard}$$

---

## 2. Project Directory Structure

All files reside strictly within the `day2/` directory:

```text
day2/
Γö£ΓöÇΓöÇ data/
Γöé   Γö£ΓöÇΓöÇ day2_sample.csv                  # 250 sensor records (Ground truth)
Γöé   ΓööΓöÇΓöÇ day2_sample.py                   # Sensor telemetry generator script
Γö£ΓöÇΓöÇ templates/
Γöé   ΓööΓöÇΓöÇ index.html                       # Operator dashboard UI (Jinja2 / HTML5)
Γö£ΓöÇΓöÇ static/
Γöé   ΓööΓöÇΓöÇ style.css                        # Industrial dark-theme CSS & animations
Γö£ΓöÇΓöÇ results/
Γöé   Γö£ΓöÇΓöÇ confusion_matrix.png             # Multiclass confusion matrix plot
Γöé   Γö£ΓöÇΓöÇ feature_importance.png           # Gini feature importance ranking chart
Γöé   ΓööΓöÇΓöÇ evaluation_report.txt            # Detailed precision/recall/F1 metrics
Γö£ΓöÇΓöÇ train_model.py                       # ML model training, evaluation & export
Γö£ΓöÇΓöÇ app.py                               # Flask web server, Decision & Action engine
Γö£ΓöÇΓöÇ predict_machine.py                   # Standalone diagnostic inference CLI
Γö£ΓöÇΓöÇ predictive_maintenance_model.joblib  # Trained Random Forest pipeline bundle
Γö£ΓöÇΓöÇ alerts.csv                           # Persistent audit trail of actions & alerts
Γö£ΓöÇΓöÇ system.log                           # Security rejection & system event log
Γö£ΓöÇΓöÇ requirements.txt                     # Python package dependencies
ΓööΓöÇΓöÇ README.md                            # Comprehensive technical documentation
```

---

## 3. Dataset Description

- **Dataset Path:** [`day2/data/day2_sample.csv`](data/day2_sample.csv)
- **Total Records:** 250 time-indexed industrial samples (200 train / 50 test)
- **Input Features:**
  - `temperature` (┬░C): Nominal range 55.0 ΓÇô 70.0 ┬░C.
  - `pressure` (bar): Nominal range 4.0 ΓÇô 6.5 bar.
  - `vibration` (mm/s): Nominal range 1.0 ΓÇô 3.5 mm/s.
  - `current` (A): Nominal range 8.0 ΓÇô 16.0 A.
  - `rpm` (RPM): Nominal range 1400 ΓÇô 2200 RPM.
- **Target Feature:** `state` (Categorical ground-truth condition)
- **Class Proportions:**
  - `NORMAL`: 162 samples (64.8%) ΓÇö Nominal operation
  - `MOTOR_OVERLOAD`: 34 samples (13.6%) ΓÇö Current draw > 16.0 A
  - `OVERHEATING`: 27 samples (10.8%) ΓÇö Machine temperature > 70.0 ┬░C
  - `LOW_PRESSURE`: 15 samples (6.0%) ΓÇö Line pressure < 4.0 bar
  - `HIGH_VIBRATION`: 12 samples (4.8%) ΓÇö Mechanical vibration > 3.5 mm/s

---

## 4. Machine Learning Model & Training

The model is structured as a leak-free **scikit-learn Pipeline**:
```text
Raw Sensor Telemetry
       Γöé
       Γû╝
[SimpleImputer]          (Median imputation for missing values)
       Γöé
       Γû╝
[StandardScaler]         (Feature normalization to zero mean, unit variance)
       Γöé
       Γû╝
[RandomForestClassifier] (200 Estimators, max_depth=12, class_weight='balanced')
```

### Key Training Highlights:
1. **Leak-Free Preprocessing:** All imputers and scalers are fitted strictly on the training partition (`X_train`) and transformed on the test partition (`X_test`).
2. **Stratified Splitting:** Uses an 80/20 train/test split with stratification (`stratify=y, random_state=42`) ensuring underrepresented fault modes (`HIGH_VIBRATION`, `LOW_PRESSURE`) are proportionally evaluated.
3. **Imbalance Compensation:** `class_weight='balanced'` automatically assigns higher penalization weights to minority fault classes.
4. **Cross-Validation:** 5-Fold Stratified Cross-Validation on the training partition confirms generalization stability.

---

## 5. Model Evaluation Results

### Performance on Held-Out Test Set (50 samples):

| Machine Condition | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| **HIGH_VIBRATION** | 1.0000 | **1.0000** | 1.0000 | 2 |
| **LOW_PRESSURE** | 1.0000 | **1.0000** | 1.0000 | 3 |
| **MOTOR_OVERLOAD** | 1.0000 | **1.0000** | 1.0000 | 7 |
| **NORMAL** | 1.0000 | **1.0000** | 1.0000 | 33 |
| **OVERHEATING** | 1.0000 | **1.0000** | 1.0000 | 5 |
| **Overall Accuracy** | ΓÇö | ΓÇö | **1.0000 (100.0%)** | 50 |
| **Macro Average** | 1.0000 | **1.0000** | **1.0000** | 50 |
| **Weighted Average** | 1.0000 | **1.0000** | **1.0000** | 50 |

### 5-Fold Stratified Cross Validation (Training Set - 200 samples):
- **CV Accuracy:** `0.9900 (+/- 0.0122)`
- **CV Macro F1:** `0.9794 (+/- 0.0279)`

### Sensor Feature Importance Ranking:
1. **`current`**: 25.13% (motor electrical load)
2. **`temperature`**: 24.30% (thermal friction and coolant efficacy)
3. **`pressure`**: 23.97% (line seal integrity and hydraulic pressure)
4. **`vibration`**: 23.51% (mechanical bearing wear and dynamic balance)
5. **`rpm`**: 3.09% (baseline motor speed)

> [!IMPORTANT]
> **Why Failure Recall Matters Most:** In industrial automation, **Recall on fault classes is significantly more critical than overall Accuracy**. A false alarm incurs a brief inspection check, whereas a missed failure (`False Negative`) causes catastrophic machine destruction, safety hazards, and factory downtime. The trained model achieves **100% Failure Recall**.

---

## 6. Decision & Action Engine

The system implements decision logic mapping machine conditions to actionable three-tier severity classifications:

```python
def predict_status(sensor_data):
    # Predicts condition using predictive_maintenance_model.joblib
    ...

def make_decision(status):
    # Evaluates predicted condition and assigns operational severity & protocol
    ...
```

### Operational Action Protocols:

| Condition | Severity | Decision Action | Recommended Technical Protocol |
| :--- | :---: | :--- | :--- |
| `NORMAL` | **Normal** | Log reading and continue monitoring | Nominal operation. Continue scheduled production batch. |
| `LOW_PRESSURE` | **Warning** | Generate maintenance inspection warning | Inspect pneumatic/hydraulic supply lines, compressor, and check-valves. |
| `MOTOR_OVERLOAD` | **Warning** | Generate maintenance inspection warning | Verify mechanical load for jamming, check winding insulation and VFD. |
| `OVERHEATING` | **Failure** | Critical alert & immediate inspection | Inspect coolant flow, radiator fins, lubricant level, and throttle motor. |
| `HIGH_VIBRATION` | **Failure** | Critical alert & immediate inspection | Inspect shaft alignment, dynamic balance, and mounting bolt tightness. |

### Action Engine & Persistent Audit Trail:
- Each evaluated reading triggers `take_action()`, which logs the event to [`day2/alerts.csv`](alerts.csv).
- Recorded fields: `timestamp`, `temperature`, `pressure`, `vibration`, `current`, `rpm`, `status`, `severity`, `action_taken`.
- Actions are simulated, visible, and safe for educational demonstration without hazardous external machinery shutdown.

---

## 7. Web Dashboard

A lightweight Flask web dashboard is provided in `day2/app.py`:

- **Real-Time Machine Health Status:** Current machine state, three-tier status badge, and model confidence percentage.
- **Live Sensor Telemetry Display:** Temperature, pressure, vibration, current, and RPM gauges with nominal safety thresholds.
- **Interactive Inference Form:** Allows operators to input custom sensor readings and execute immediate diagnosis.
- **Scenario Presets:** One-click presets to simulate Normal, Overheating, Low Pressure, High Vibration, and Motor Overload.
- **Dataset Sample Tester:** Button to pick and evaluate random records directly from `day2/data/day2_sample.csv`.
- **Model Metrics Panel:** Displays live test accuracy, cross-validation metrics, per-class precision/recall, and Gini feature importances.
- **Audit Alert History:** Displays the 10 most recent maintenance alerts from `alerts.csv` with a clear-log control.

---

## 8. Security Validation & Safe Error Handling

To ensure robust and safe demonstration execution:

1. **Input Completeness:** Verifies that all 5 required sensor fields are present.
2. **Numeric Type Enforcement:** Rejects non-numeric characters (e.g. text or strings) gracefully.
3. **Physical Non-Negativity Checks:** Reject impossible negative values (such as negative pressure, negative vibration, or negative current).
4. **Demonstration Safety Bounds:** Enforces plausible physical ranges:
   - Temperature: $0.0 \text{ to } 200.0^\circ\text{C}$
   - Pressure: $0.0 \text{ to } 20.0\text{ bar}$
   - Vibration: $0.0 \text{ to } 30.0\text{ mm/s}$
   - Current: $0.0 \text{ to } 60.0\text{ A}$
   - RPM: $0 \text{ to } 5000\text{ RPM}$
5. **No Invalid Data In Model:** Input validation runs before any data reaches the scikit-learn pipeline.
6. **Graceful Error Handling:** Missing model files or CSV read errors are caught cleanly without server crashes.
7. **Security Event Logging:** All rejected inputs, missing fields, and system errors are logged with timestamps to [`day2/system.log`](system.log).
8. **Dual-Layer Validation:** Inputs are validated on the client side in JavaScript and re-validated server-side in Python.
9. **Safe HTTP Methods:** State-modifying actions (alerts, clearing logs, sampling) strictly require HTTP `POST` requests.

---

## 9. Installation & Execution Guide

Run the following commands from PowerShell or terminal:

```powershell
# 1. Navigate into day2 folder
cd day2

# 2. Install required dependencies
python -m pip install -r requirements.txt

# 3. Train the Random Forest ML Model
python train_model.py

# 4. Start the Web Dashboard
python app.py
```

Open your web browser and navigate to:
```text
http://127.0.0.1:5000
```

### Optional: Standalone CLI Diagnostic Tool
You can also run predictions from the command line:

```powershell
# Run 5 demonstration fault scenarios:
python predict_machine.py --demo

# Test custom telemetry:
python predict_machine.py --temperature 85.5 --pressure 5.0 --vibration 2.1 --current 12.0 --rpm 1800

# Interactive prompt:
python predict_machine.py --interactive
```

---

## 10. Known Scientific Limitations

1. **Threshold-Derived Labels:**  
   The target states in `day2_sample.csv` were originally assigned using fixed physical thresholds (e.g., Temperature > 70┬░C). Consequently, the Random Forest model is learning non-linear decision boundaries that approximate these operational rules rather than learning natural physics-based degradation patterns.
2. **Diagnostic vs. Prognostic:**  
   This model performs **condition classification / anomaly diagnosis** of the machine's current state. For true **prognostic predictive maintenance** (forecasting future failures hours or days in advance), the system would require:
   - Time-to-Failure (TTF) and Remaining Useful Life (RUL) target metrics.
   - Run-to-failure historical sensor logs with progressive degradation over time.
   - Temporal walk-forward validation rather than random stratified splits.
3. **Demonstration Safety:**  
   All automated actions in this project are simulated and logged. In industrial production environments, emergency shutdowns must be handled by fail-safe hardware interlocks rather than standalone software models.
