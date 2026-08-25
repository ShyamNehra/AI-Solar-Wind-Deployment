import pandas as pd

# Load training dataset
df = pd.read_csv("app/ml/training_data.csv")

print("\n========== UNIQUE VALUES ==========\n")

# Show how many unique values each column has
print(df.nunique())

print("\n========== SAMPLE DATA ==========\n")

# Show first 10 rows
print(df.head(10))