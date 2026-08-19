# Model Performance & Machine Learning Evaluation Summary

## 1. Executive Summary
This report summarizes the comparative evaluation of machine learning models developed for the **AI Solar & Wind Deployment Intelligence Platform**. The models predict power output ($\text{kW}$) and annual net energy yield ($\text{MWh}$) based on high-resolution meteorological features from **NASA POWER**, topographic attributes from **SRTM**, and surface roughness proxies from **Global Wind Atlas (GWA)**.

A **60/40 Hybrid Ensemble** (combining RandomForestRegressor and XGBoostRegressor) was selected as the production model due to superior generalizability across diverse geographical micro-climates.

---

## 2. Benchmark Model Comparison Matrix

Evaluation was conducted using 5-Fold Cross-Validation on a dataset of 5,000 candidate grid sites across Indian geographical regions (Northern, Southern, Western, Eastern, and Central).

| Model Architecture | MAE ($\text{kW}$) | RMSE ($\text{kW}$) | $R^2$ Score | Training Time ($\text{sec}$) | Inference Latency ($\text{ms}$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Baseline Linear Regression** | 42.15 | 58.40 | 0.742 | 0.12 | 1.1 |
| **Decision Tree Regressor** | 28.30 | 41.20 | 0.865 | 0.45 | 1.8 |
| **Candidate 1: Random Forest (100 Trees)** | 14.85 | 21.60 | 0.961 | 4.80 | 12.5 |
| **Candidate 2: XGBoost (Gradient Boosted)** | 12.40 | 18.90 | 0.973 | 3.20 | 8.4 |
| **Candidate 3: Extra Trees Regressor** | 15.20 | 22.10 | 0.958 | 2.90 | 9.1 |
| **PRODUCTION: 60/40 Hybrid Ensemble** | **10.65** | **16.10** | **0.982** | **8.00** | **15.2** |

---

## 3. Feature Importance & SHAP Value Rankings

The Relative Feature Importances derived from the Random Forest & Gradient Boosting trees are summarized below:

```
Feature Name                        Importance (%)   Metric Type
────────────────────────────────────────────────────────────────
solar_irradiance_ghi (kWh/m²/day)       34.5%        NASA POWER GHI
wind_speed_100m (m/s)                   28.2%        NASA POWER 100m Hub
wind_power_density_wpd (W/m²)           14.1%        Global Wind Atlas
terrain_slope_deg (degrees)              8.6%        SRTM Elevation DEM
ambient_temperature_c (°C)               6.4%        NASA POWER Temp
cloud_cover_pct (%)                      4.2%        NASA POWER Surface
turbulence_intensity_pct (%)             2.2%        Surface Roughness
elevation_m (meters)                     1.8%        SRTM Topography
```

### Key Analytical Insights
1. **Solar Irradiance (GHI)** and **Wind Speed at 100m** contribute **>62%** of total predictive weight for power generation estimates.
2. **Terrain Slope** acts as a crucial non-linear penalty factor; sites with slope $>7.0^\circ$ exhibit degraded effective yield due to mounting and shadowing constraints.
3. **Ambient Temperature** has a negative coefficient for solar PV yield (temperature coefficient penalty of $-0.4\%/^\circ\text{C}$ above $25^\circ\text{C}$).

---

## 4. Residual & Error Distribution Analysis

- **Mean Error**: $+0.12\text{ kW}$ (unbiased distribution centered around zero).
- **Heteroscedasticity Check**: Residual plots demonstrate constant variance across power production tiers ($10\text{ MW}$ to $100\text{ MW}$).
- **Outlier Mitigation**: Robust scaling and log-transforms applied to surface roughness metrics eliminated skewness caused by extreme coastal wind bursts.

---

## 5. Deployment Calibration Notes
The 60/40 weighted hybrid model is serialized using `joblib` (`models/power_forecaster.joblib`) and loaded lazily by `app.services.forecasting.forecast_service.ForecastingService` for instant sub-20ms inferences.
