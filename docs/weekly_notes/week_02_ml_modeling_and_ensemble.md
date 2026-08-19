# Week 02 Development Log: ML Modeling & Ensembling

## 1. Objectives & Scope
- Develop regression pipelines for predicting system power output ($\text{kW}$) and net annual yield ($\text{MWh}$).
- Compare baseline models (Linear Regression, Decision Tree, Random Forest, XGBoost).
- Calibrate a **60/40 Hybrid Ensemble** model combining Random Forest and XGBoost.

---

## 2. Key Accomplishments

### Feature Engineering & Modeling
- Engineered PV temperature derating loss factor ($0.4\%/^\circ\text{C}$ penalty above STC $25^\circ\text{C}$).
- Engineered Wind Power Density ($\text{WPD} = 0.5 \cdot \rho \cdot v^3$) feature.
- Applied 5-Fold Cross-Validation across candidate grid coordinates.

### Benchmark Results
- **Linear Regression**: $R^2 = 0.742$, $\text{MAE} = 42.15\text{ kW}$
- **Random Forest**: $R^2 = 0.961$, $\text{MAE} = 14.85\text{ kW}$
- **XGBoost Regressor**: $R^2 = 0.973$, $\text{MAE} = 12.40\text{ kW}$
- **60/40 Hybrid Ensemble**: **$R^2 = 0.982$**, **$\text{MAE} = 10.65\text{ kW}$**

---

## 3. Serialization & Integration
- Serialized optimal ensemble model artifact using `joblib` (`models/power_forecaster.joblib`).
- Integrated model with `ForecastingService` for fast sub-20ms backend inferences.
