# Application Module Mapping & Traceability Matrix

## 1. System High-Level Module Traceability

The **AI Solar & Wind Deployment Intelligence Platform** is structured as an end-to-end decoupled system. Below is the mapping of components from the User Interface down to database storage models.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Frontend Layer (React 18 + Vite)                                         │
│    • SiteAnalysisScreen.jsx  ──► Interactive Site Dashboard & Control Panel  │
│    • SiteMap.jsx              ──► Spatial Visualizer & Lat/Lng Selector     │
│    • SiteCompare.jsx          ──► Multi-Site Side-by-Side Comparison        │
│    • src/api/client.js        ──► Central Axios HTTP Client (JWT Interceptor)│
│    • src/api/analysis.js      ──► Pipeline API Service Invocations          │
│    • src/api/sites.js         ──► Team Saved Sites Management Service       │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ HTTP / REST Payload
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. Gateway Security & Middleware Layer                                      │
│    • app/core/security_middleware.py ──► OWASP Security Headers Guard   │
│    • app/core/rate_limiter.py       ──► SlowAPI IP-Based Rate Limiter       │
│    • app/auth/dependencies.py        ──► Bearer JWT Authorization Injector  │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ Validated Request
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. Backend API Router Tier (FastAPI)                                        │
│    • app/api/predictions.py ──► /predictions/full-analysis, /forecast       │
│    • app/api/saved_sites.py ──► /sites/saved (GET, POST, DELETE)            │
│    • app/api/projects.py    ──► /projects (Workspace Project Management)    │
│    • app/auth/router.py     ──► /auth/login, /auth/register, /auth/me        │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ Service Execution
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. Domain & Analytics Services Engine                                       │
│    • app/services/analysis_pipeline.py ──► Central Pipeline Orchestrator    │
│    • app/services/nasa_power_service.py──► NASA POWER Meteorological Fetch │
│    • app/evaluation/scorer.py          ──► Multi-Criteria Suitability Scorer│
│    • app/evaluation/constraints.py     ──► Spatial Buffer & Slope Screening │
│    • app/services/forecasting_service.py─► ML Generation Forecasting       │
│    • app/services/financial_service.py ──► 25-Yr NPV/IRR/LCOE Valuation     │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ ORM Persistence
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. Database Storage Layer (SQLAlchemy ORM + SQLite / PostgreSQL)            │
│    • app/models/user.py               ──► User & Role Credentials           │
│    • app/models/project.py            ──► Team Projects                     │
│    • app/models/site.py               ──► Site Records & Coordinates        │
│    • app/models/saved_site.py         ──► Favorite Workspace Sites          │
│    • app/models/prediction.py         ──► Forecasted Inferences             │
│    • app/models/environmental_data.py ──► NASA POWER Climate Records        │
│    • app/models/suitability_score.py  ──► MCDA Score Breakdown             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. End-to-End Data Flow Mapping

### Execution Flow: Site Assessment & ML Yield Prediction

1. **User Action**: User clicks a point on `SiteMap.jsx` or enters coordinates on `SiteAnalysisScreen.jsx` and clicks "Run Analysis".
2. **Frontend Request**: `src/api/analysis.js::runFullSiteAnalysis()` sends POST request to `/predictions/full-analysis`.
3. **Gateway Verification**:
   - `app/core/security_middleware.py` attaches OWASP security headers.
   - `app/core/rate_limiter.py` verifies request is within 20 requests/minute compute limit.
4. **Router Dispatch**: `app/api/predictions.py::execute_full_standardized_analysis()` delegates request to `app/services/analysis_pipeline.py`.
5. **Data Orchestration**:
   - `nasa_power_service.py` fetches solar GHI ($\text{kWh/m}^2/\text{day}$) and $100\text{m}$ wind speed ($\text{m/s}$).
   - `constraints.py` checks slope angle and 150m river exclusion buffers.
   - `scorer.py` evaluates 0-100 MCDA category scores.
   - `forecasting_service.py` executes RandomForest inference (`models/power_forecaster.joblib`).
   - `financial_service.py` calculates 25-year NPV, IRR %, LCOE, and payback period.
6. **Persistence**: Evaluation, climate data, and predictions are auto-persisted to `environmental_data`, `predictions`, and `suitability_scores` DB tables via SQLAlchemy.
7. **Response & Rendering**: Standardized JSON payload returned to frontend. Dashboard renders KPI tiles, energy curves, and PDF/Excel report capabilities.

---

## 3. Frontend Architecture & Directory Reconciliation

To ensure compliance with enterprise React design standards, the frontend leverages an **Adapter/Facade Pattern**:
- **`src/pages/`**: Serves as entrypoints for React Router routes.
- **`src/components/`**: Manages modular UI elements, authentication workflows, spatial Leaflet canvas, and live assessment state.
- **`src/services/`**: Aggregates business logic, unified API networking services, and client-side export helpers.

### Module Reconciliation Table

| Required Directory File | Actual Implementation / Target | Architectural Purpose |
| :--- | :--- | :--- |
| `frontend/src/pages/DashboardPage.jsx` | `frontend/src/components/SiteAnalysisScreen.jsx` | Top-level route container hosting interactive map & live assessment cards. |
| `frontend/src/pages/LoginPage.jsx` | `frontend/src/components/auth/LoginPage.jsx` | Route view wrapping user login form and authentication state. |
| `frontend/src/pages/RegisterPage.jsx` | `frontend/src/components/auth/RegisterPage.jsx` | Route view wrapping registration and validation handlers. |
| `frontend/src/services/apiService.js` | `frontend/src/api/` (`client.js`, `analysis.js`, `sites.js`, `auth.js`) | Unified API service facade aggregating all backend communication. |
| `frontend/src/services/exportService.js` | Standalone utility functions | Report download handler (CSV export with UTF-8 BOM, JSON export, PDF print). |

