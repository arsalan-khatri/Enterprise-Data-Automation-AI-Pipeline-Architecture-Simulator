import pandas as pd

# 1. Load the dataset you generated in Chunk 1
try:
    print("Loading raw customer tickets...")
    df = pd.read_csv('data/raw/customer_tickets.csv')
except FileNotFoundError:
    print("Error: 'customer_tickets.csv' not found. Please ensure the file is in the same folder.")
    exit()

# 2. Rule-Based Sentiment Generation (Simulating Past LLM / Human Tagging)
negative_keywords = ['late', 'delayed', 'stuck', 'cancel', 'failed', 'broken', 'twice', 'error', 'wrong', 'damaged', 'frustrating', 'unacceptable', 'urgent', 'asap', 'disappointed', 'terrible']
positive_keywords = ['thanks', 'love', 'great', 'awesome', 'appreciate', 'satisfied', 'good']

def assign_sentiment(text):
    text_lower = str(text).lower()
    if any(word in text_lower for word in negative_keywords):
        return 'Negative'
    elif any(word in text_lower for word in positive_keywords):
        return 'Positive'
    return 'Neutral'

print("Assigning Sentiments based on message context...")
df['sentiment'] = df['message'].apply(assign_sentiment)

# 3. Rule-Based Priority Generation (Business Logic)
def calculate_priority(row):
    score = 0
    
    # Rule A: Customer Tier
    if row['customer_type'] == 'VIP': score += 3
    elif row['customer_type'] == 'Premium': score += 2
    else: score += 1
        
    # Rule B: Order Value Risk
    if row['order_value'] > 100000: score += 3
    elif row['order_value'] > 50000: score += 2
    else: score += 1
        
    # Rule C: Churn Risk (Previous Complaints)
    if row['previous_complaints'] >= 3: score += 3
    elif row['previous_complaints'] > 0: score += 1
        
    # Rule D: Emotional State (Sentiment)
    if row['sentiment'] == 'Negative': score += 2
    elif row['sentiment'] == 'Positive': score -= 1
        
    # Priority Matrix Mapping
    if score >= 9: return 'Critical'
    elif score >= 7: return 'High'
    elif score >= 5: return 'Medium'
    else: return 'Low'

print("Calculating Priorities based on business rules...")
df['priority'] = df.apply(calculate_priority, axis=1)

# 4. Save the Final Labeled Dataset
output_file = 'customer_tickets_labeled.csv'
df.to_csv(output_file, index=False)

print(f"\n✅ Success! Data labeled and saved as '{output_file}'.")

# 5. Display a quick audit
print("\n--- Priority Distribution ---")
print(df['priority'].value_counts())
print("\n--- Sentiment Distribution ---")
print(df['sentiment'].value_counts())