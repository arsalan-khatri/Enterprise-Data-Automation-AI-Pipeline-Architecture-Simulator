import pandas as pd

# Dataset load karo
file_path = "../raw/customer_tickets.csv"

df = pd.read_csv(file_path)

print("\n" + "=" * 60)
print("CUSTOMER SUPPORT DATASET CHECK")
print("=" * 60)

# 1. Total records
print(f"\nTotal Records: {len(df):,}")

# 2. Total columns
print(f"Total Columns: {len(df.columns)}")

# 3. Columns
print("\nColumns:")
for column in df.columns:
    print(f" - {column}")

# 4. Missing values
print("\nMissing Values:")
print(df.isnull().sum())

# 5. Duplicate rows
print(f"\nDuplicate Rows: {df.duplicated().sum()}")

# 6. Duplicate ticket IDs
print(f"Duplicate Ticket IDs: {df['ticket_id'].duplicated().sum()}")

# 7. Unique customer types
print("\nCustomer Types:")
print(df["customer_type"].value_counts())

# 8. Status distribution
print("\nTicket Status:")
print(df["status"].value_counts())

# 9. Department distribution
print("\nDepartments:")
print(df["department"].value_counts())

# 10. Order value statistics
print("\nOrder Value:")
print(df["order_value"].describe())

# 11. Message length
df["message_length"] = df["message"].astype(str).str.len()

print("\nMessage Length:")
print(df["message_length"].describe())

print("\n" + "=" * 60)
print("DATA CHECK COMPLETED")
print("=" * 60)