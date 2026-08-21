# Platform System Architecture Specification

## 1. Executive System Overview

The **AI Solar & Wind Deployment Intelligence Platform** is built on a multi-tiered micro-service-ready architecture. It orchestrates real-time satellite climatology, spatial multi-criteria decision analysis (MCDA), machine learning generation forecasting, and investment appraisal into a responsive web dashboard.

---

## 2. Multi-Tier Architecture Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PRESENTATION TIER (Frontend - React 18 + Vite)                              │
│ • State Management: AuthContext (JWT) + Local Storage Workspace Cache       │
│ • Mapping Engine: Custom GIS Visualizer & Leaflet Coordinate Selector       │
│ • Exporter: Multi-section CSV UTF-8 BOM & Formatted Engineering PDF Engine  │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ HTTP / JSON Payload
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ GATEWAY & SECURITY TIER (FastAPI + SlowAPI + Middleware)                    │
│ • OWASP Security Headers (X-Frame-Options DENY, HSTS, CSP Policy)          │
│ • Rate Limiting: 5 req/min (Auth), 20 req/min (Compute), 120 req/min (API)  │
│ • Auth Guard: PyJWT / Jose HS256 Token Validation                           │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ Validated Request Context
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ BUSINESS LOGIC & ANALYTICS TIER (FastAPI Services)                          │
│ • Pipeline Orchestrator: analysis_pipeline.py                               │
│ • Climatology Service: nasa_power_service.py (GHI, Wind, Temp)              │
│ • GIS & Spatial Screening: constraints.py (Slope < 15°, 150m River Buffer)  │
│ • Multi-Criteria Scoring: scorer.py (0-100 Suitability Index)               │
│ • ML Power Forecasting: forecasting_service.py (RandomForest Regressor)     │
│ • Investment Valuation: financial_service.py (NPV, IRR, LCOE, Payback)      │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ ORM Persistence
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PERSISTENCE & DATA TIER (SQLAlchemy ORM)                                    │
│ • SQLite / PostgreSQL Engine (app.db / solar_wind.db)                       │
│ • Models: User, Project, Site, SavedSite, RecentSite, Prediction            │
│ • Sync: Team Workspace Cloud Synchronization across all devices             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Multi-Criteria Decision Making (MCDM) Logic

Site suitability is computed using a 2-stage evaluation framework:

### Stage 1: Binary Exclusion Screening (Hard Constraints)
If any condition below is met, the site status is set to **`REJECTED`**:
- **Slope Angle**: Terrain slope $> 15.0^\circ$.
- **River Proximity**: Distance to water body $< 150\text{m}$.
- **Ecological Reserve**: Inside national park or protected sanctuary boundary ($< 500\text{m}$).
- **Residential Encroachment**: Within $300\text{m}$ of dense urban settlements.

### Stage 2: Composite Suitability Index (Soft Scoring: 0 - 100)
For sites passing hard constraints:

$$S = 0.35 \cdot S_{\text{resource}} + 0.20 \cdot S_{\text{terrain}} + 0.20 \cdot S_{\text{infra}} + 0.10 \cdot S_{\text{env}} + 0.15 \cdot S_{\text{econ}}$$

- **$S_{\text{resource}}$**: Scaled from GHI ($\text{kWh/m}^2/\text{day}$) and 100m Wind Speed ($\text{m/s}$).
- **$S_{\text{terrain}}$**: Linear penalty based on slope angle.
- **$S_{\text{infra}}$**: Proximity to power grid substations ($<5\text{ km}$) and logistics roads.
- **$S_{\text{econ}}$**: Projected Return on Investment (ROI %).

---

## 4. Machine Learning Forecasting Pipeline

The forecasting pipeline utilizes a **60/40 Weighted Hybrid Ensemble** consisting of a **Random Forest Regressor** and **XGBoost Regressor** trained on 5,000 regional site profiles.

- **Inputs**: Solar GHI, 100m Wind Speed, WPD, Slope, Ambient Temperature, Capacity MW.
- **Outputs**: Monthly energy curves ($\text{MWh}$), Net Annual Yield ($\text{MWh}$ & $\text{GWh}$), Capacity Factor ($\text{CF} \%$).
- **Latency**: Sub-20ms inference using pre-compiled `joblib` artifacts.
