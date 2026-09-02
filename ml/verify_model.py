import os
import joblib
import pandas as pd

from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# ============================================================
# CONFIG
# ============================================================

DATASET_PATH = "../data/final_data/customer_tickets_balanced.csv"
MODEL_PATH = "saved_models/priority_model.pkl"

# Agar encoders separate files mein save kiye hain,
# in paths ko apne actual filenames ke mutabiq change karna.
ENCODERS_PATH = "saved_models/label_encoders.pkl"

# ============================================================
# 1. LOAD DATASET
# ============================================================

print("\n" + "=" * 65)
print("MODEL VERIFICATION")
print("=" * 65)

print("\n1. Loading dataset...")

df = pd.read_csv(DATASET_PATH)

print(f"Dataset size: {len(df):,} rows")

# ============================================================
# 2. FEATURES AND TARGET
# ============================================================

features = [
    "customer_type",
    "order_value",
    "previous_complaints",
    "department",
    "sentiment"
]

target = "priority"

X = df[features].copy()
y = df[target].copy()

# ============================================================
# 3. LOAD SAVED MODEL
# ============================================================

print("\n2. Loading saved Random Forest model...")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Model not found: {MODEL_PATH}"
    )

model = joblib.load(MODEL_PATH)

print("Model loaded successfully.")

# ============================================================
# 4. LOAD ENCODERS
# ============================================================

print("\n3. Loading encoders...")

if not os.path.exists(ENCODERS_PATH):
    raise FileNotFoundError(
        f"Encoders not found: {ENCODERS_PATH}"
    )

encoders = joblib.load(ENCODERS_PATH)

print("Encoders loaded successfully.")

# ============================================================
# 5. APPLY SAME ENCODING
# ============================================================

categorical_columns = [
    "customer_type",
    "department",
    "sentiment"
]

for column in categorical_columns:

    encoder = encoders[column]

    X[column] = encoder.transform(
        X[column]
    )

# ============================================================
# 6. TEST SAVED MODEL
# ============================================================

print("\n4. Testing saved model...")

predictions = model.predict(X)

accuracy = accuracy_score(
    y,
    predictions
)

print(f"\nAccuracy on complete dataset: {accuracy * 100:.2f}%")

print("\nClassification Report:")

print(
    classification_report(
        y,
        predictions
    )
)

# ============================================================
# 7. CONFUSION MATRIX
# ============================================================

print("\n5. Confusion Matrix:")

labels = sorted(y.unique())

cm = confusion_matrix(
    y,
    predictions,
    labels=labels
)

print("\nLabels:")
print(labels)

print("\nMatrix:")
print(cm)

# ============================================================
# 8. FEATURE IMPORTANCE
# ============================================================

print("\n6. Feature Importance:")

if hasattr(model, "feature_importances_"):

    importance = pd.DataFrame({
        "feature": features,
        "importance": model.feature_importances_
    })

    importance = importance.sort_values(
        by="importance",
        ascending=False
    )

    print(
        importance.to_string(
            index=False
        )
    )

else:

    print(
        "This model does not provide feature_importances_."
    )

# ============================================================
# 9. CROSS VALIDATION
# ============================================================

print("\n7. Running 5-Fold Cross Validation...")

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

cv_results = cross_validate(
    model,
    X,
    y,
    cv=cv,
    scoring=[
        "accuracy",
        "precision_weighted",
        "recall_weighted",
        "f1_weighted"
    ],
    n_jobs=-1
)

print(
    f"\nCV Accuracy: "
    f"{cv_results['test_accuracy'].mean() * 100:.2f}% "
    f"+/- "
    f"{cv_results['test_accuracy'].std() * 100:.2f}%"
)

print(
    f"CV Precision: "
    f"{cv_results['test_precision_weighted'].mean() * 100:.2f}%"
)

print(
    f"CV Recall: "
    f"{cv_results['test_recall_weighted'].mean() * 100:.2f}%"
)

print(
    f"CV F1: "
    f"{cv_results['test_f1_weighted'].mean() * 100:.2f}%"
)

# ============================================================
# 10. MANUAL UNSEEN TEST CASES
# ============================================================

print("\n8. Testing manual unseen cases...")

test_cases = pd.DataFrame([
    {
        "customer_type": "Regular",
        "order_value": 5000,
        "previous_complaints": 0,
        "department": "Sales",
        "sentiment": "Positive"
    },

    {
        "customer_type": "Regular",
        "order_value": 20000,
        "previous_complaints": 1,
        "department": "Logistics",
        "sentiment": "Neutral"
    },

    {
        "customer_type": "Premium",
        "order_value": 120000,
        "previous_complaints": 3,
        "department": "Payments",
        "sentiment": "Negative"
    },

    {
        "customer_type": "Business",
        "order_value": 300000,
        "previous_complaints": 5,
        "department": "Technical Support",
        "sentiment": "Negative"
    }
])

encoded_cases = test_cases.copy()

for column in categorical_columns:

    encoder = encoders[column]

    encoded_cases[column] = encoder.transform(
        encoded_cases[column]
    )

manual_predictions = model.predict(
    encoded_cases[features]
)

print("\nManual Predictions:")

for i, prediction in enumerate(
    manual_predictions
):

    print(
        f"Case {i + 1}: "
        f"{prediction}"
    )

# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 65)
print("MODEL VERIFICATION COMPLETED")
print("=" * 65)