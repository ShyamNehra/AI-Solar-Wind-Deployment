"""
Unit test suite for Time-Series Forecasting module.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.auth.auth_handler import create_access_token
from app.forecasting.data_loader import TimeSeriesDataLoader
from app.forecasting.feature_engineering import TimeSeriesFeatureEngine
from app.forecasting.solar_forecast import SolarForecaster
from app.forecasting.wind_forecast import WindForecaster
from app.forecasting.hybrid_forecast import HybridForecaster
from app.forecasting.forecasting_service import ForecastingService

client = TestClient(app)

def get_auth_header():
    token = create_access_token(data={"sub": "admin", "role": "Administrator"})
    return {"Authorization": f"Bearer {token}"}

def test_data_loader():
    loader = TimeSeriesDataLoader()
    data = loader.load_historical_data(latitude=26.9124, longitude=75.7873, days=14)
    assert len(data) == 14
    assert "date" in data[0]
    assert "solar_irradiance" in data[0]
    assert "wind_speed" in data[0]

def test_feature_engineering():
    loader = TimeSeriesDataLoader()
    engine = TimeSeriesFeatureEngine()
    raw = loader.load_historical_data(days=7)
    enriched = engine.transform(raw)
    assert len(enriched) == 7
    assert "year" in enriched[0]
    assert "month" in enriched[0]
    assert "day_of_year" in enriched[0]
    assert "season" in enriched[0]
    assert "is_weekend" in enriched[0]
    assert "is_leap_year" in enriched[0]

def test_solar_forecaster():
    loader = TimeSeriesDataLoader()
    raw = loader.load_historical_data(days=14)
    forecaster = SolarForecaster()
    res = forecaster.forecast(raw, horizon_days=7, installed_capacity_mw=50.0)
    assert res["prediction_status"] == "Completed"
    assert res["predicted_solar_irradiance"] > 0
    assert res["predicted_energy_generation"] > 0
    assert len(res["forecast_points"]) == 7

def test_wind_forecaster():
    loader = TimeSeriesDataLoader()
    raw = loader.load_historical_data(days=14)
    forecaster = WindForecaster()
    res = forecaster.forecast(raw, horizon_days=7, installed_capacity_mw=50.0)
    assert res["prediction_status"] == "Completed"
    assert res["predicted_wind_speed"] > 0
    assert res["predicted_energy_generation"] > 0
    assert len(res["forecast_points"]) == 7

def test_hybrid_forecaster():
    loader = TimeSeriesDataLoader()
    raw = loader.load_historical_data(days=14)
    forecaster = HybridForecaster()
    res = forecaster.forecast(raw, horizon_days=7, solar_capacity_mw=30.0, wind_capacity_mw=20.0)
    assert res["prediction_status"] == "Completed"
    assert res["predicted_energy_generation"] > 0
    assert len(res["forecast_points"]) == 7

def test_forecasting_apis():
    headers = get_auth_header()
    
    # Solar GET & POST
    res = client.get("/forecast/solar?latitude=26.9124&longitude=75.7873&horizon_days=7", headers=headers)
    assert res.status_code == 200
    assert res.json()["prediction_status"] == "Completed"

    res_post = client.post("/forecast/solar", json={"latitude": 26.9124, "longitude": 75.7873, "horizon_days": 7}, headers=headers)
    assert res_post.status_code == 200

    # Wind GET & POST
    res_w = client.get("/forecast/wind?latitude=8.0883&longitude=77.5385&horizon_days=7", headers=headers)
    assert res_w.status_code == 200
    assert res_w.json()["prediction_status"] == "Completed"

    # Hybrid GET & POST
    res_h = client.get("/forecast/hybrid?latitude=26.9124&longitude=75.7873&horizon_days=7", headers=headers)
    assert res_h.status_code == 200
    assert res_h.json()["prediction_status"] == "Completed"
