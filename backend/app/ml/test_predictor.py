from app.ml.predictor import Predictor

predictor = Predictor()

sample_features = [
    12.5,        # Slope
    450,         # Elevation
    18,          # TurbulenceIntensity
    29.5,        # Air Temperature
    65,          # Relative Humidity
    1200,        # Precipitation
    6.8,         # Wind Speed
    14.2,        # Wind Gust
    1012,        # Air Pressure
    5.4,         # Annual Solar
    0.45,        # NDVI
    0.20,        # NDBI
    0.10,        # NDWI
    31.2,        # LST
    420,         # City Elevation
    2500000,     # Population
    5600         # District Area
]

result = predictor.predict(sample_features)

print(result)