from app.ml.model_loader import ModelLoader


model1 = ModelLoader.load_model()
model2 = ModelLoader.load_model()

print(model1)
print()

print("Same object :", model1 is model2)