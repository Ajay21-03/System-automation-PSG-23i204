"""
DAY 2 ┬╖ Industrial Predictive Maintenance Inference System
23IF02 System Automation ΓÇö PSG Tech

Provides dynamic machine condition detection using the trained
Random Forest model artifact (predictive_maintenance_model.joblib).

Can be used both as a standalone script (CLI / Interactive)
and as an importable module:
    from predict_machine import detect_status

    status = detect_status({"temperature": 85.0, "pressure": 5.0, "vibration": 2.0, "current": 12.0, "rpm": 1800})
    print(status)  # "OVERHEATING"
"""

import argparse
from pathlib import Path
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent / "predictive_maintenance_model.joblib"

# Actionable Industrial Maintenance Protocols
RECOMMENDATIONS = {
    "NORMAL": (
        "STATUS: NORMAL OPERATION\n"
        "ΓÇó All telemetry parameters are within nominal operating limits.\n"
        "ΓÇó Protocol: Continue standard production cycle. Maintain routine scheduled inspection log."
    ),
    "OVERHEATING": (
        "STATUS: OVERHEATING DETECTED\n"
        "ΓÇó Critical thermal buildup observed (> 70┬░C).\n"
        "ΓÇó Protocol: Inspect cooling system flow, radiator fins, coolant levels, and lubricant viscosity.\n"
        "ΓÇó Safety: Throttle machine load or schedule thermal stabilization before component warping."
    ),
    "LOW_PRESSURE": (
        "STATUS: LOW SYSTEM PRESSURE DETECTED\n"
        "ΓÇó Pressure dropped below safe operating limit (< 4.0 bar).\n"
        "ΓÇó Protocol: Inspect pneumatic/hydraulic supply lines, compressor manifold, seals, and check-valves.\n"
        "ΓÇó Safety: Check for fluid leaks or pump cavitation before loss of hydraulic clamping force."
    ),
    "HIGH_VIBRATION": (
        "STATUS: HIGH MECHANICAL VIBRATION DETECTED\n"
        "ΓÇó Vibration amplitude exceeded safe mechanical tolerance (> 3.5 mm/s).\n"
        "ΓÇó Protocol: Inspect shaft alignment, dynamic unbalance, bearing race wear, and foundation bolts.\n"
        "ΓÇó Safety: Risk of catastrophic bearing seizure or mechanical fatigue failure."
    ),
    "MOTOR_OVERLOAD": (
        "STATUS: MOTOR OVERLOAD / OVERCURRENT DETECTED\n"
        "ΓÇó Electrical current draw exceeds rated capacity (> 16.0 A).\n"
        "ΓÇó Protocol: Inspect driven load for mechanical jamming, check winding insulation, and VFD settings.\n"
        "ΓÇó Safety: Risk of stator winding burnout or breaker trip under continuous overload."
    ),
}

# Cache model in memory for fast repeated inference
_CACHED_MODEL = None


def load_model(model_path: Path = MODEL_PATH):
    """Load and cache the trained model pipeline bundle."""
    global _CACHED_MODEL
    if _CACHED_MODEL is not None:
        return _CACHED_MODEL

    if not model_path.exists():
        raise FileNotFoundError(
            f"Trained model artifact not found at {model_path}.\n"
            f"Please run 'python day2/train_model.py' first."
        )

    artifact = joblib.load(model_path)
    _CACHED_MODEL = (artifact["pipeline"], artifact["feature_names"], artifact["classes"])
    return _CACHED_MODEL


def validate_readings(readings: dict | list | tuple) -> dict:
    """Normalize and validate sensor inputs into standard dictionary format."""
    feature_order = ["temperature", "pressure", "vibration", "current", "rpm"]

    # 1. Handle list / tuple inputs
    if isinstance(readings, (list, tuple)):
        if len(readings) != 5:
            raise ValueError(f"Expected 5 sensor readings [temp, pressure, vibration, current, rpm], got {len(readings)}")
        clean = dict(zip(feature_order, readings))
    # 2. Handle dict inputs
    elif isinstance(readings, dict):
        clean = {}
        for f in feature_order:
            if f not in readings:
                raise KeyError(f"Missing required sensor reading: '{f}'")
            clean[f] = readings[f]
    else:
        raise TypeError("Readings must be passed as a dictionary, list, or tuple.")

    # 3. Numeric conversions & bounds verification
    try:
        clean_dict = {
            "temperature": float(clean["temperature"]),
            "pressure": float(clean["pressure"]),
            "vibration": float(clean["vibration"]),
            "current": float(clean["current"]),
            "rpm": int(clean["rpm"]),
        }
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid non-numeric sensor reading: {e}")

    return clean_dict


def detect_status(readings: dict | list | tuple, model_path: Path = MODEL_PATH) -> str:
    """Primary API: Pass sensor readings, returns detected machine status string.

    Example:
        >>> detect_status({"temperature": 85.0, "pressure": 5.0, "vibration": 2.0, "current": 12.0, "rpm": 1800})
        'OVERHEATING'
    """
    clean = validate_readings(readings)
    pipeline, feature_names, _ = load_model(model_path)

    input_df = pd.DataFrame([[clean[f] for f in feature_names]], columns=feature_names)
    predicted_class = pipeline.predict(input_df)[0]
    return str(predicted_class)


def predict_condition(readings: dict | list | tuple, model_path: Path = MODEL_PATH) -> tuple[str, dict]:
    """Run full inference diagnostic, print formatted summary, and return (status, probabilities)."""
    clean = validate_readings(readings)
    pipeline, feature_names, classes = load_model(model_path)

    input_df = pd.DataFrame([[clean[f] for f in feature_names]], columns=feature_names)

    predicted_status = pipeline.predict(input_df)[0]
    probabilities = pipeline.predict_proba(input_df)[0]
    prob_dict = {cls: float(prob) for cls, prob in zip(classes, probabilities)}

    confidence = prob_dict[predicted_status] * 100.0

    print("\n" + "=" * 65)
    print("INDUSTRIAL PREDICTIVE MAINTENANCE ΓÇö INFERENCE DIAGNOSTIC")
    print("=" * 65)
    print("INPUT SENSOR READINGS:")
    print(f"  ΓÇó Temperature: {clean['temperature']:6.2f} ┬░C")
    print(f"  ΓÇó Pressure:    {clean['pressure']:6.2f} bar")
    print(f"  ΓÇó Vibration:   {clean['vibration']:6.2f} mm/s")
    print(f"  ΓÇó Current:     {clean['current']:6.2f} A")
    print(f"  ΓÇó RPM:         {clean['rpm']:6d} RPM")
    print("-" * 65)
    print(f"DETECTED MACHINE STATUS: >>> {predicted_status} <<<")
    print(f"MODEL CONFIDENCE:        {confidence:.2f}%")
    print("-" * 65)
    print("CONDITION PROBABILITY DISTRIBUTION:")
    for cls in sorted(prob_dict.keys(), key=lambda c: prob_dict[c], reverse=True):
        bar = "#" * int(prob_dict[cls] * 25)
        print(f"  {cls:16s}: {prob_dict[cls] * 100:5.1f}%  {bar}")
    print("-" * 65)
    print("RECOMMENDED ACTION PROTOCOL:")
    print(RECOMMENDATIONS.get(predicted_status, "No action protocol defined."))
    print("=" * 65 + "\n")

    return predicted_status, prob_dict


def interactive_mode():
    """Interactive prompt for operators to type readings directly."""
    print("\n=== ENTER MACHINE SENSOR READINGS TO DETECT STATUS ===")
    try:
        t = input("  1. Temperature (┬░C) [e.g. 65.0]: ").strip() or "65.0"
        p = input("  2. Pressure (bar)     [e.g. 5.2]:  ").strip() or "5.2"
        v = input("  3. Vibration (mm/s)   [e.g. 2.1]:  ").strip() or "2.1"
        c = input("  4. Current (A)        [e.g. 11.5]: ").strip() or "11.5"
        r = input("  5. RPM                [e.g. 1800]: ").strip() or "1800"

        predict_condition([t, p, v, c, r])
    except KeyboardInterrupt:
        print("\n[!] Exited by user.")
    except Exception as e:
        print(f"[ERROR] {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Predict industrial machine status from passed sensor readings."
    )
    # Support positional arguments: python predict_machine.py 85 5.2 2.1 12 1800
    parser.add_argument(
        "readings",
        nargs="*",
        type=float,
        help="5 positional readings: temperature pressure vibration current rpm",
    )
    # Support named arguments: python predict_machine.py --temperature 85 ...
    parser.add_argument("--temperature", type=float, help="Temperature in ┬░C")
    parser.add_argument("--pressure", type=float, help="Pressure in bar")
    parser.add_argument("--vibration", type=float, help="Vibration in mm/s")
    parser.add_argument("--current", type=float, help="Current in A")
    parser.add_argument("--rpm", type=int, help="Motor RPM")
    parser.add_argument("--demo", action="store_true", help="Run 5 demonstration scenarios")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive prompt")

    args = parser.parse_args()

    # 1. Positional arguments mode: python predict_machine.py 85 5.2 2.1 12 1800
    if len(args.readings) == 5:
        predict_condition(args.readings)
        return
    elif len(args.readings) > 0 and len(args.readings) != 5:
        print(f"[ERROR] Expected exactly 5 sensor values, got {len(args.readings)}: {args.readings}")
        print("Usage: python predict_machine.py <temperature> <pressure> <vibration> <current> <rpm>")
        sys.exit(1)

    # 2. Flag arguments mode: python predict_machine.py --temperature 85 ...
    flag_vals = [args.temperature, args.pressure, args.vibration, args.current, args.rpm]
    if any(v is not None for v in flag_vals):
        if None in flag_vals:
            print("[ERROR] When using flag options, all 5 sensor readings must be provided:")
            print("        --temperature, --pressure, --vibration, --current, --rpm")
            sys.exit(1)
        predict_condition(flag_vals)
        return

    # 3. Demo mode
    if args.demo:
        demo_cases = [
            ("Nominal Normal Run", [63.5, 5.2, 2.1, 11.8, 1820]),
            ("Overheating Event",  [86.4, 5.1, 2.3, 12.0, 1800]),
            ("Low Pressure Event", [62.0, 2.4, 2.2, 12.1, 1810]),
            ("High Vibration Event",[64.0, 5.0, 7.4, 11.5, 1780]),
            ("Motor Overload Event",[65.0, 5.2, 2.5, 24.5, 1650]),
        ]
        print("\n=== RUNNING 5 INDUSTRIAL DEMONSTRATION SCENARIOS ===")
        for name, vals in demo_cases:
            print(f">>> TEST SCENARIO: {name}")
            predict_condition(vals)
        return

    # 4. Interactive mode (or default prompt)
    interactive_mode()


if __name__ == "__main__":
    main()
