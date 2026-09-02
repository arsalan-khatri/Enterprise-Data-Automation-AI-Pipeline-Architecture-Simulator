import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import os

print("1. Loading the balanced dataset...")
df = pd.read_csv('../data/final_data/customer_tickets_balanced.csv')

# 2. Feature Selection (Exactly as you designed)
features = ['customer_type', 'order_value', 'previous_complaints', 'department', 'sentiment']
X = df[features].copy()
y = df['priority'].copy()

print("2. Engineering Features (Encoding text to numbers)...")
encoders = {}
for col in ['customer_type', 'department', 'sentiment']:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col])
    encoders[col] = le

# 3. Train/Test Split (80% Train, 20% Test)
print("3. Splitting data into Train and Test sets...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Model Training
print("4. Training Random Forest Classifier...")
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# 5. Evaluation
print("5. Evaluating Model Performance...\n")
y_pred = rf_model.predict(X_test)

print(f"✅ Overall Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%\n")
print("📊 Classification Report (F1, Precision, Recall):")
print(classification_report(y_test, y_pred))

print("🧩 Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# 6. Save Model and Encoders for Production (FastAPI / n8n)
os.makedirs('saved_models', exist_ok=True)
joblib.dump(rf_model, 'saved_models/priority_model.pkl')
joblib.dump(encoders, 'saved_models/label_encoders.pkl')
print("\n💾 Model and Encoders saved successfully in 'saved_models/' directory!")