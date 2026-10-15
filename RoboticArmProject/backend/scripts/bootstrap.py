"""
Bootstrap script: generate dataset, validate, train model.
Run: python scripts/bootstrap.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.dataset_generator import generate, save_dataset, load_dataset
from app.services.dataset_validator import validate
from app.services.ml_service import train
from app.services.persistence import init_db

def main():
    os.makedirs("data", exist_ok=True)
    os.makedirs("models_ml", exist_ok=True)

    init_db()
    print("Database initialised.")

    print("\nGenerating 5,000-row dataset...")
    df = generate(n_rows=5000)
    result = save_dataset(df)
    rows = result["rows"]
    dist = result["class_distribution"]
    print(f"Saved: {rows} rows -> {result['path']}")
    print(f"Class distribution: {dist}")

    print("\nValidating dataset...")
    v = validate()
    print(f"Validation passed: {v['passed']}")
    for c in v["checks"]:
        status = "OK  " if c["passed"] else "FAIL"
        print(f"  [{status}] {c['check']}: {c['detail']}")

    print("\nTraining Random Forest model...")
    m = train(df)
    acc   = m["accuracy"]
    mf1   = m["macro_f1"]
    mp    = m["macro_precision"]
    mr    = m["macro_recall"]
    trn   = m["train_size"]
    tst   = m["test_size"]
    print(f"Model trained!")
    print(f"  Accuracy:         {acc:.4f}")
    print(f"  Macro F1:         {mf1:.4f}")
    print(f"  Macro Precision:  {mp:.4f}")
    print(f"  Macro Recall:     {mr:.4f}")
    print(f"  Train / Test:     {trn} / {tst}")
    print("  Per-class metrics:")
    for cls, info in m["per_class"].items():
        pr = info["precision"]
        rc = info["recall"]
        f1 = info["f1"]
        sp = info["support"]
        print(f"    {cls:10s}  P={pr:.3f}  R={rc:.3f}  F1={f1:.3f}  support={sp}")
    print("  Feature importance:")
    for feat, imp in sorted(m["feature_importance"].items(), key=lambda x: -x[1]):
        print(f"    {feat:15s}: {imp:.4f}")
    print(f"\nModel saved to: {m.get('trained_at','')}")
    print("\nBootstrap complete. Run: python run.py")

if __name__ == "__main__":
    main()
