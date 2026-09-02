import pandas as pd
import random
from faker import Faker

fake = Faker()

# 1. Load the existing labeled dataset
print("Loading existing dataset...")
df = pd.read_csv('../raw/customer_tickets_labeled.csv')

# Target numbers to add
targets = {
    'Medium': 1667,
    'High': 4161,
    'Critical': 5156
}

# Dictionaries for matching sentiments to text
negative_msgs = ["This is unacceptable, my order is late.", "I am very disappointed and frustrated.", "The item arrived damaged.", "Cancel my order immediately, terrible service.", "Payment failed but money deducted twice!"]
neutral_msgs = ["I want to know the delivery status.", "How do I return this item?", "Can you help me update my account?", "I have a question about my recent order.", "When will this product be restocked?"]
positive_msgs = ["Thanks for the quick support!", "Great product, I love it.", "Awesome service, really appreciate it.", "Very satisfied with my purchase.", "Good quality, thank you!"]

departments = ['Logistics', 'Finance', 'Quality Assurance', 'IT Support', 'Customer Success', 'Sales']

# The same scoring logic we used before
def get_priority_score(c_type, o_val, p_comp, sent):
    score = 0
    if c_type == 'VIP': score += 3
    elif c_type == 'Premium': score += 2
    else: score += 1
        
    if o_val > 100000: score += 3
    elif o_val > 50000: score += 2
    else: score += 1
        
    if p_comp >= 3: score += 3
    elif p_comp > 0: score += 1
        
    if sent == 'Negative': score += 2
    elif sent == 'Positive': score -= 1
        
    if score >= 9: return 'Critical'
    elif score >= 7: return 'High'
    elif score >= 5: return 'Medium'
    else: return 'Low'

new_records = []
current_id = 20000 # Starting new ticket IDs from T20000

print("Generating synthetic balanced data... This will take a few seconds.")

for target_priority, count in targets.items():
    print(f"Generating {count} '{target_priority}' tickets...")
    added = 0
    
    while added < count:
        # Generate random features
        c_type = random.choice(['VIP', 'Premium', 'Regular'])
        o_val = random.randint(1000, 150000)
        p_comp = random.randint(0, 5)
        sent = random.choice(['Negative', 'Neutral', 'Positive'])
        
        # Check if these random features create the priority we need right now
        calculated_priority = get_priority_score(c_type, o_val, p_comp, sent)
        
        if calculated_priority == target_priority:
            # We found a match! Let's create the full record
            if sent == 'Negative': msg = random.choice(negative_msgs)
            elif sent == 'Positive': msg = random.choice(positive_msgs)
            else: msg = random.choice(neutral_msgs)
                
            new_records.append({
                'ticket_id': f"T{current_id}",
                'customer_id': f"C{random.randint(1000, 5000)}",
                'message': msg,
                'created_at': fake.date_time_between(start_date='-6M', end_date='now').strftime("%Y-%m-%d %H:%M:%S"),
                'customer_type': c_type,
                'order_value': o_val,
                'previous_complaints': p_comp,
                'department': random.choice(departments),
                'status': random.choice(['Open', 'In Progress', 'Resolved']),
                'sentiment': sent,
                'priority': calculated_priority
            })
            added += 1
            current_id += 1

# 2. Append to existing dataframe and save
new_df = pd.DataFrame(new_records)
balanced_df = pd.concat([df, new_df], ignore_index=True)

output_file = '../final_data/customer_tickets_balanced.csv'
balanced_df.to_csv(output_file, index=False)

print(f"\n✅ Success! Added 10,984 new tickets. Total records are now {len(balanced_df)}.")
print(f"Data saved as '{output_file}'.")

print("\n--- NEW Perfectly Balanced Priority Distribution ---")
print(balanced_df['priority'].value_counts())