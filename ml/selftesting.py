import pandas as pd
import joblib

print("1. Loading Model and Encoders...")
# Make sure the paths point to your saved_models folder
model = joblib.load('saved_models/priority_model.pkl')
encoders = joblib.load('saved_models/label_encoders.pkl')

print("2. Creating Custom Ticket Data...")
# Create a dummy dataframe for our custom test case
custom_ticket = pd.DataFrame([{
    'customer_type': 'Regular',          # 'VIP', 'Premium', 'Regular'
    'order_value': 120000,               # Any integer
    'previous_complaints': 1,            # Any integer
    'department': 'Sales',           # Use any existing department name
    'sentiment': 'Neutral'              # 'Negative', 'Neutral', 'Positive'
}])

print("\n--- Raw Input ---")
print(custom_ticket.to_markdown(index=False))

print("\n3. Encoding Features...")
# Loop through categorical columns and apply the saved encoders
for col in ['customer_type', 'department', 'sentiment']:
    custom_ticket[col] = encoders[col].transform(custom_ticket[col])

print("\n4. Running Prediction...")
prediction = model.predict(custom_ticket)

print("\n========================================")
print(f"🔥 PREDICTED PRIORITY: {prediction[0]}")
print("========================================")