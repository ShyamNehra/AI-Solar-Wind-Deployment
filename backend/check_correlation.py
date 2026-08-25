import pandas as pd

df = pd.read_csv("app/ml/training_data.csv")

df["Label"] = df["Label"].map({
    "Yes": 1,
    "No": 0
})

print(df.corr(numeric_only=True)["Label"].sort_values(ascending=False))