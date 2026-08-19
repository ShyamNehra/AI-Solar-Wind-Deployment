# AI Solar & Wind Deployment Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.0.0-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.4.0-646CFF.svg)](https://vitejs.dev/)
[![Security](https://img.shields.io/badge/Security-OWASP%20Certified-success.svg)](#security-specifications)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, full-stack renewable energy deployment intelligence platform designed for rapid site suitability assessment, high-resolution **NASA POWER** climate integration, machine learning power generation forecasting (**RandomForest**), spatial exclusion constraint compliance, and 25-year financial appraisal for utility-scale solar, wind, and hybrid renewable energy projects.

---

## Key Features & Architecture Highlights

### Geographic & Spatial Intelligence
- **Coordinate-Driven Site Evaluation**: Real-time lat/lng site evaluation with interactive map visualizer, digital elevation modeling (SRTM), and slope calculation.
- **Exclusion Zone & Geofence Audit**: Automated screening against hard environmental constraints, protected areas, ecological buffers, and logistics route distances.

### Meteorological Integration Engine (NASA POWER)
- **Real-Time Data Fetching**: Retrieves Global Horizontal Irradiance (GHI, $\text{kWh/m}^2/\text{day}$), Peak Sun Hours, 100m Hub-height Wind Velocity ($\text{m/s}$), Wind Power Density ($\text{W/m}^2$), Ambient Temperature, and Cloud Cover.

### Machine Learning Energy Forecasting
- **Scikit-Learn RandomForest Pipeline**: Delivers 12-month seasonal generation curves, applied capacity factors (CF %), system efficiency losses, and annual net energy yields ($\text{MWh}$ / $\text{GWh}$).

### 25-Year Investment & Financial Appraisal Engine
- Automated valuation computing:
  - **CAPEX & OPEX** (Capital & Operational Expenditure in INR ₹)
  - **PPA Tariff Revenue** ($\text{INR } ₹/\text{kWh}$)
  - **Net Present Value (NPV)** over 25-year lifecycle
  - **Internal Rate of Return (IRR %)** & **Return on Investment (ROI %)**
  - **Levelized Cost of Energy (LCOE)** ($\text{INR } ₹/\text{kWh}$)
  - **Simple Payback Period** (Years)

### Enterprise Role-Based Access Control (RBAC) & Security
- **Role Profiles**: Custom views for *Renewable Energy Planners*, *GIS Analysts*, *Project Managers*, and *Platform Administrators*.
- **OWASP Protection**: Rate limiting with **SlowAPI** (brute-force defense), JWT Bearer authentication, OWASP HTTP security headers (`X-Frame-Options`, `CSP`, `HSTS`), and Pydantic input bounds validation.

### 100% Fully Responsive Cross-Device UI/UX Architecture
- **Universal Mobile & Tablet Optimization**: Ultra-sleek, adaptive design system engineered for flawless performance across desktop ultra-wides, laptops, tablets, and smartphones (iOS & Android).
- **Mobile Header Action Bar & Quick Controls**: Dedicated mobile navigation featuring an instant **Favorite Sites (`★`)** popover manager positioned directly to the left of the notification bell (`🔔`), touch-optimized 42px touch targets, and mobile-hide rules for decorative banners.
- **Sleek Minimal Key-Value Card Cards**: Adaptive 2-column key-value grids with muted grey vertical center dividers on desktop/tablet viewports, automatically collapsing to clean single-column cards on mobile viewports with **100% zero data loss**.

### Exhaustive Engineering PDF & Excel Exports
- **1-Click Comprehensive Reporting**: Exports UTF-8 BOM 7-section CSV financial sheets and multi-page PDF engineering dossiers containing complete site metrics, financial matrices, and strategic AI recommendations.

---

## System Architecture

```mermaid
flowchart TD
    subgraph Client ["Frontend (React 18 + Vite)"]
        UI[Interactive UI & Map Visualizer]
        AuthCtx[Auth & Role State Context]
        ExportEngine[PDF & Excel Export Engine]
    end

    subgraph Middleware ["Security & Gateway Layer"]
        CORS[CORS Restrictions]
        Limiter[SlowAPI Rate Limiter]
        SecHeaders[OWASP Security Headers]
        JWTAuth[JWT Bearer Guard]
    end

    subgraph Backend ["Backend Engine (FastAPI + Python 3.11)"]
        API[FastAPI Router Modules]
        Pipeline[Site Analysis Pipeline]
        MLService[RandomForest ML Forecast Engine]
        Scorer[Multi-Criteria Suitability Scorer]
        FinService[Financial Appraisal Service]
    end

    subgraph Storage ["Persistence Layer"]
        DB[(SQLite / SQLAlchemy ORM)]
    end

    subgraph External ["External Data Sources"]
        NASA[NASA POWER Climate API]
        SRTM[SRTM Topography Engine]
    end

    UI -->|HTTPS / JSON| Security Headers
    Security Headers --> Limiter --> JWTAuth --> API
    API --> Pipeline
    Pipeline --> NASA
    Pipeline --> SRTM
    Pipeline --> MLService
    Pipeline --> Scorer
    Pipeline --> FinService
    API --> DB
```

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend UI** | React 18, Vite 5, Axios, Lucide Icons, 100% Cross-Device Responsive Vanilla CSS Design System |
| **Backend Framework** | Python 3.11, FastAPI 0.110, Uvicorn, Pydantic v2 |
| **Machine Learning** | Scikit-Learn (RandomForestRegressor), Pandas, NumPy, Joblib |
| **Security & Auth** | SlowAPI (Rate Limiter), PyJWT / Jose, Passlib (Bcrypt), Security Headers Middleware |
| **Database & ORM** | SQLite, SQLAlchemy 2.0 ORM |
| **External APIs** | NASA POWER Agro-Climatology API, OpenStreetMap / Overpass GIS |

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: `>= 3.11`
- **Node.js**: `>= 18.0.0`
- **npm**: `>= 9.0.0`

---

### 1. Backend Setup & Startup

```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python -m venv ..\.venv

# Activate virtual environment (Windows PowerShell)
..\.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r requirements.txt

# Run database table migrations
python scripts/migrate_users.py

# Seed default team workspace users
python scripts/seed_users.py

# Start FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend server will start at `http://localhost:8000`. API Swagger Docs available at `http://localhost:8000/docs`.

---

### 2. Frontend Setup & Startup

Open a new terminal window:

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start Vite dev server
npm run dev
```

The frontend application will launch at `http://localhost:5173`.

---

## Default Demo Accounts

| Role | Username | Password | Team Code |
| :--- | :--- | :--- | :--- |
| **Administrator** | `shyam_nehra` | `password123` | `1001` |
| **Renewable Energy Planner** | `aishwarya_r` | `planner123` | `1001` |
| **GIS Analyst** | `gis_analyst` | `gis123` | `1001` |
| **Project Manager** | `rajesh_kumar` | `pm123` | `1001` |

---

## Security Specifications

- **Authentication Guard**: JWT Bearer tokens with 24-hour expiration (`HS256`).
- **Rate Limiting**:
  - `/auth/login`: 5 requests / min (prevents credential stuffing)
  - `/predictions/full-analysis`: 20 requests / min (prevents compute resource abuse)
  - General API: 120 requests / min
- **OWASP Security Headers**:
  - `X-Frame-Options: DENY` (anti-clickjacking)
  - `X-Content-Type-Options: nosniff` (MIME sniffing guard)
  - `Strict-Transport-Security` (HSTS)
  - `Content-Security-Policy` (CSP policy)
- **Input Sanitization**: Pydantic input length and coordinate range validation (Latitude: $-90^\circ$ to $+90^\circ$, Longitude: $-180^\circ$ to $+180^\circ$).

---

## Repository Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/             # REST Endpoints (auth, predictions, sites, projects)
│   │   ├── auth/            # Auth models, JWT security, RBAC dependencies
│   │   ├── core/            # Security headers & SlowAPI rate limiters
│   │   ├── database/        # SQLAlchemy engine & session setup
│   │   ├── evaluation/      # Scorer & spatial constraint evaluation engine
│   │   ├── models/          # ORM models (User, Site, Project, Predictions)
│   │   └── services/        # ML forecasting & financial appraisal services
│   ├── scripts/             # DB migration & seed scripts
│   ├── requirements.txt     # Python dependency manifest
│   └── main.py              # FastAPI server entry point
├── frontend/
│   ├── src/
│   │   ├── api/             # Authenticated Axios client & API endpoints
│   │   ├── components/      # React components (SiteAnalysisScreen, Map, Compare)
│   │   ├── context/         # AuthContext state provider
│   │   └── App.jsx          # Route manager
│   └── package.json         # Node.js dependencies
└── README.md
```

---

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.
