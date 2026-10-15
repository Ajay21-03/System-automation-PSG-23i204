"""
DAY 2 ┬╖ Random Forest Predictive Maintenance Model Training
23IF02 System Automation ΓÇö PSG Tech

This script trains, validates, evaluates, and exports an industrial
Predictive Maintenance Random Forest Classifier using day2_sample.csv.
"""

from pathlib import Path
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "day2_sample.csv"
RESULTS_DIR = BASE_DIR / "results"
MODEL_PATH = BASE_DIR / "predictive_maintenance_model.joblib"

# Guarantee results directory exists
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def inspect_dataset(df: pd.DataFrame):
    """Perform exploratory inspection of the industrial sensor dataset."""
    print("=" * 70)
    print("1. DATASET INSPECTION")
    print("=" * 70)
    print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Columns: {list(df.columns)}")
    print("\nData Types & Non-Null Counts:")
    print(df.dtypes)
    
    missing_counts = df.isnull().sum()
    print(f"\nMissing values per column:\n{missing_counts[missing_counts > 0] if missing_counts.sum() > 0 else 'None (0 missing)'}")
    
    duplicates = df.duplicated().sum()
    print(f"Duplicate records: {duplicates}")

    if "state" not in df.columns:
        raise ValueError("Target column 'state' not found in dataset!")

    print("\nClass Distribution (Target: 'state'):")
    class_dist = df["state"].value_counts()
    for state, count in class_dist.items():
        pct = (count / len(df)) * 100
        print(f"  - {state:16s}: {count:3d} ({pct:.1f}%)")
    
    print("\nNumerical Feature Summary Statistics:")
    features = [c for c in df.columns if c != "state"]
    print(df[features].describe().round(2).T[["mean", "std", "min", "50%", "max"]])
    print("=" * 70 + "\n")


def train_and_evaluate():
    """Train Random Forest pipeline, run validation, and export artifacts."""
    if not DATA_PATH.exists():
        print(f"[ERROR] Dataset not found at: {DATA_PATH}")
        sys.exit(1)

    # 1. Load dataset
    df = pd.read_csv(DATA_PATH)
    inspect_dataset(df)

    # 2. Features and Target separation
    target_col = "state"
    feature_cols = ["temperature", "pressure", "vibration", "current", "rpm"]

    # Verify columns exist
    missing_cols = [c for c in feature_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required feature columns: {missing_cols}")

    X = df[feature_cols].copy()
    y = df[target_col].copy()

    # 3. Stratified Train / Test Split (prevent data leakage, preserve class balance)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    print("=" * 70)
    print("2. DATASET PARTITIONING")
    print("=" * 70)
    print(f"Training Samples: {len(X_train)} ({len(X_train)/len(df)*100:.1f}%)")
    print(f"Testing Samples:  {len(X_test)} ({len(X_test)/len(df)*100:.1f}%)")
    print("\nClass Counts in Training Set:")
    print(y_train.value_counts().to_dict())
    print("Class Counts in Test Set:")
    print(y_test.value_counts().to_dict())
    print("=" * 70 + "\n")

    # 4. Pipeline with Preprocessing & Model
    # Imputer handles potential missing values; Scaler standardizes features;
    # class_weight='balanced' offsets the majority NORMAL class.
    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("classifier", RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced",
            max_depth=12,
            min_samples_split=2,
            min_samples_leaf=1,
            n_jobs=-1,
        )),
    ])

    # 5. Stratified Cross-Validation on Training Data (Leak-free)
    print("=" * 70)
    print("3. STRATIFIED 5-FOLD CROSS VALIDATION (TRAIN SET)")
    print("=" * 70)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_acc = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="accuracy")
    cv_f1 = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="f1_macro")
    print(f"CV Accuracy: Mean = {cv_acc.mean():.4f} (+/- {cv_acc.std():.4f})")
    print(f"CV Macro F1: Mean = {cv_f1.mean():.4f} (+/- {cv_f1.std():.4f})")
    print("=" * 70 + "\n")

    # 6. Fit Final Model on Full Training Set
    pipeline.fit(X_train, y_train)

    # 7. Model Evaluation
    y_train_pred = pipeline.predict(X_train)
    y_test_pred = pipeline.predict(X_test)

    train_acc = accuracy_score(y_train, y_train_pred)
    test_acc = accuracy_score(y_test, y_test_pred)

    prec_macro = precision_score(y_test, y_test_pred, average="macro", zero_division=0)
    rec_macro = recall_score(y_test, y_test_pred, average="macro", zero_division=0)
    f1_macro = f1_score(y_test, y_test_pred, average="macro", zero_division=0)

    prec_weighted = precision_score(y_test, y_test_pred, average="weighted", zero_division=0)
    rec_weighted = recall_score(y_test, y_test_pred, average="weighted", zero_division=0)
    f1_weighted = f1_score(y_test, y_test_pred, average="weighted", zero_division=0)

    classes = np.unique(y)
    report_text = classification_report(y_test, y_test_pred, target_names=classes, zero_division=0)
    cm = confusion_matrix(y_test, y_test_pred, labels=classes)

    print("=" * 70)
    print("4. EVALUATION METRICS (HELD-OUT TEST SET)")
    print("=" * 70)
    print(f"Training Accuracy: {train_acc * 100:.2f}%")
    print(f"Testing Accuracy:  {test_acc * 100:.2f}%")
    print(f"Accuracy Gap (Train - Test): {(train_acc - test_acc) * 100:.2f}% (Overfitting check)")
    print("-" * 70)
    print(f"Macro Precision:   {prec_macro:.4f}")
    print(f"Macro Recall:      {rec_macro:.4f}")
    print(f"Macro F1-Score:    {f1_macro:.4f}")
    print("-" * 70)
    print(f"Weighted Precision:{prec_weighted:.4f}")
    print(f"Weighted Recall:   {rec_weighted:.4f}")
    print(f"Weighted F1-Score: {f1_weighted:.4f}")
    print("-" * 70)
    print("\nDetailed Per-Class Classification Report:")
    print(report_text)
    print("=" * 70 + "\n")

    # 8. Feature Importances
    rf_model: RandomForestClassifier = pipeline.named_steps["classifier"]
    importances = rf_model.feature_importances_
    feat_ranking = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)

    print("=" * 70)
    print("5. SENSOR FEATURE IMPORTANCE RANKING")
    print("=" * 70)
    for rank, (feat, imp) in enumerate(feat_ranking, start=1):
        bar = "#" * int(imp * 40)
        print(f"  {rank}. {feat:12s}: {imp:.4f} ({imp*100:5.2f}%) {bar}")
    print("=" * 70 + "\n")

    # 9. Plot and Save Visualizations
    # A) Confusion Matrix
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        xticklabels=classes,
        yticklabels=classes,
        title="Predictive Maintenance Confusion Matrix",
        ylabel="True Machine Condition",
        xlabel="Predicted Machine Condition",
    )
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right", rotation_mode="anchor")

    # Annotate numbers in confusion matrix cells
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j,
                i,
                format(cm[i, j], "d"),
                ha="center",
                va="center",
                color="white" if cm[i, j] > thresh else "black",
                fontweight="bold",
            )
    fig.tight_layout()
    cm_plot_path = RESULTS_DIR / "confusion_matrix.png"
    plt.savefig(cm_plot_path, dpi=300)
    plt.close()
    print(f"[+] Saved confusion matrix image to: {cm_plot_path}")

    # B) Feature Importance Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    feats, imps = zip(*reversed(feat_ranking))
    ax.barh(feats, imps, color="#1f77b4")
    ax.set_xlabel("Gini Feature Importance")
    ax.set_title("Sensor Feature Importance in Random Forest")
    fig.tight_layout()
    fi_plot_path = RESULTS_DIR / "feature_importance.png"
    plt.savefig(fi_plot_path, dpi=300)
    plt.close()
    print(f"[+] Saved feature importance chart to: {fi_plot_path}")

    # 10. Save Evaluation Report to Text File
    report_file = RESULTS_DIR / "evaluation_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("INDUSTRIAL PREDICTIVE MAINTENANCE ΓÇö EVALUATION REPORT\n")
        f.write("=====================================================\n\n")
        f.write(f"Dataset: {DATA_PATH}\n")
        f.write(f"Total Samples: {len(df)}\n")
        f.write(f"Training Samples: {len(X_train)} | Test Samples: {len(X_test)}\n\n")
        f.write(f"Train Accuracy: {train_acc * 100:.2f}%\n")
        f.write(f"Test Accuracy:  {test_acc * 100:.2f}%\n")
        f.write(f"Macro F1-Score: {f1_macro:.4f}\n")
        f.write(f"Weighted F1-Score: {f1_weighted:.4f}\n\n")
        f.write("5-Fold Cross Validation (Training Set):\n")
        f.write(f"  CV Accuracy: {cv_acc.mean():.4f} +/- {cv_acc.std():.4f}\n")
        f.write(f"  CV Macro F1: {cv_f1.mean():.4f} +/- {cv_f1.std():.4f}\n\n")
        f.write("Classification Report:\n")
        f.write(report_text + "\n\n")
        f.write("Confusion Matrix:\n")
        f.write(np.array2string(cm) + "\n\n")
        f.write("Feature Importance:\n")
        for feat, imp in feat_ranking:
            f.write(f"  {feat:12s}: {imp:.4f}\n")
    print(f"[+] Saved text evaluation report to: {report_file}")

    # 11. Save Fitted Model Pipeline with Detailed Metadata
    report_dict = classification_report(y_test, y_test_pred, target_names=classes, zero_division=0, output_dict=True)
    model_artifact = {
        "pipeline": pipeline,
        "feature_names": feature_cols,
        "classes": list(classes),
        "metrics": {
            "train_accuracy": float(train_acc),
            "test_accuracy": float(test_acc),
            "macro_precision": float(prec_macro),
            "macro_recall": float(rec_macro),
            "macro_f1": float(f1_macro),
            "weighted_f1": float(f1_weighted),
            "cv_accuracy_mean": float(cv_acc.mean()),
            "cv_accuracy_std": float(cv_acc.std()),
            "cv_f1_mean": float(cv_f1.mean()),
            "cv_f1_std": float(cv_f1.std()),
            "confusion_matrix": cm.tolist(),
            "classification_report": report_dict,
            "feature_importances": {feat: float(imp) for feat, imp in feat_ranking},
        },
        "description": "Random Forest Industrial Predictive Maintenance Pipeline (23IF02 System Automation)",
    }
    joblib.dump(model_artifact, MODEL_PATH)
    print(f"[+] Saved model bundle to: {MODEL_PATH}")
    print("\nTraining and evaluation pipeline completed successfully!")


if __name__ == "__main__":
    train_and_evaluate()
