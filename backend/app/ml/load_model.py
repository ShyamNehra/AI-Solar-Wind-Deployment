import os
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "random_forest_model.joblib"
)

model = joblib.load(MODEL_PATH)

print("Model loaded successfully!")
print(model)