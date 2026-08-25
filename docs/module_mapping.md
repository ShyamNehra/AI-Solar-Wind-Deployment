# Module Responsibility Mapping

## Project Title
AI-Powered Solar & Wind Deployment Intelligence Platform

---

## 1. Frontend Module

### Responsibility
- Provides the user interface.
- Displays maps, charts, and analysis results.
- Allows users to search for locations.
- Sends requests to the backend APIs.
- Shows recommended deployment sites.

### Technologies
- React
- TypeScript
- Vite
- Leaflet
- Chart.js

---

## 2. Backend Module

### Responsibility
- Handles all API requests.
- Processes user inputs.
- Performs solar and wind suitability analysis.
- Integrates GIS datasets.
- Returns processed results to the frontend.

### Technologies
- FastAPI
- Python
- Uvicorn

---

## 3. Dataset Module

### Responsibility
Stores all geospatial datasets required for analysis.

### Datasets Used
- NASA POWER (Solar Irradiance)
- Global Wind Atlas (Wind Speed)
- SRTM (Elevation)
- OpenStreetMap (Roads & Infrastructure)
- Sentinel (Satellite Imagery)

---

## 4. AI/ML Module

### Responsibility
- Predicts suitable deployment locations.
- Ranks locations based on multiple factors.
- Generates recommendations for solar and wind installations.

### Libraries
- Scikit-learn
- NumPy
- Pandas

---

## 5. GIS Processing Module

### Responsibility
- Reads raster and vector datasets.
- Combines multiple spatial layers.
- Calculates terrain characteristics.
- Performs spatial suitability analysis.

### Libraries
- GeoPandas
- Rasterio
- Shapely

---

## 6. Reports Module

### Responsibility
- Generates deployment reports.
- Summarizes analysis results.
- Stores generated reports.

---

## 7. Docker Module

### Responsibility
- Containerizes the application.
- Ensures consistent deployment.
- Manages frontend and backend services.

---

# Overall Workflow

User
↓
Frontend (React)
↓
Backend API (FastAPI)
↓
GIS Processing + AI Analysis
↓
Datasets
    ├── NASA POWER
    ├── Global Wind Atlas
    ├── SRTM
    ├── OpenStreetMap
    └── Sentinel
↓
Suitability Analysis
↓
Recommended Deployment Locations
↓
Frontend Dashboard
This document maps out the system components and module boundaries for the Solar & Wind Deployment Intelligence Platform.

---

## 1. Authentication Module
* **Responsibilities**: 
  - Manage user registration and secure login.
  - Issue JWT tokens for secure authentication.
  - Implement role-based access control (RBAC) (e.g. Admin, Analyst).
* **Inputs**: User login credentials (email, password).
* **Outputs**: Verification status, JSON Web Tokens (JWT).

---

## 2. Solar Prediction Module
* **Responsibilities**:
  - Parse NASA POWER solar dataset data.
  - Calculate solar irradiation indexes (GHI, DNI).
  - Forecast energy outputs based on historical trends and local climates.
* **Inputs**: Latitude, longitude, time range, NASA POWER API/CSV records.
* **Outputs**: Hourly/daily solar energy generation estimates (kWh).

---

## 3. Wind Prediction Module
* **Responsibilities**:
  - Process wind speed parameters (Global Wind Atlas profiles).
  - Apply wind shear equations to extrapolate wind speed at custom turbine heights.
  - Calculate power density and potential wind turbine output using energy yield models.
* **Inputs**: Wind speed columns (at 10m, 50m, 100m heights) from CSV/API.
* **Outputs**: Extrapolated wind speed profiles and projected electricity output (kWh).

---

## 4. Site Suitability Module
* **Responsibilities**:
  - Combine elevation (SRTM) and land cover (Sentinel-2) layers.
  - Apply spatial routing rules (e.g. proximity to OSM highways and power lines).
  - Compute a weighted Suitability Index (0-100 score) for hybrid wind-solar installation.
* **Inputs**: SRTM slope, Sentinel-2 classification, OSM infrastructure coordinates.
* **Outputs**: Aggregated Site Suitability Index and filtering criteria (acceptable vs. excluded areas).

---

## 5. Database Module
* **Responsibilities**:
  - Manage connection pooling with PostgreSQL.
  - Handle CRUD queries via SQL Alchemy ORM models.
  - Track database migration scripts and schema definitions.
* **Inputs**: Application requests, configuration params.
* **Outputs**: Retrieved records, commit confirmations.

---

## 6. Reports Module
* **Responsibilities**:
  - Compile tabular solar/wind prediction and site metrics into files.
  - Generate PDF summaries with embedded charts and Excel sheets for offline analysis.
* **Inputs**: Aggregated suitability indexes and power yield predictions.
* **Outputs**: Exportable PDF/XLSX files.

---

## 7. Dashboard Module (Frontend)
* **Responsibilities**:
  - Render map visualizations of target terrain and grid networks.
  - Plot interactive graphs (energy generation curves over time).
  - Provide input widgets for adjusting site optimization weights.
* **Inputs**: API responses (JSON).
* **Outputs**: Interactive User Interface (charts, maps, data grids).

---

## 8. API Services Module
* **Responsibilities**:
  - Expose REST API routing endpoints for frontend consumption.
  - Validate client payloads and handle HTTP response formats.
  - Interface between controllers and underlying modules.
* **Inputs**: HTTP requests.
* **Outputs**: HTTP JSON responses, OpenAPI specs.
---

## Authentication Module

Responsibilities

User Registration

Login

JWT Authentication

Role-Based Access

Profile Management

---

## Solar Prediction Module

Responsibilities

Solar Irradiance Analysis

Energy Prediction

Panel Efficiency

Seasonal Forecasting

---

## Wind Prediction Module

Responsibilities

Wind Speed Analysis

Power Density Prediction

Wind Energy Estimation

Forecasting

---

## Site Suitability Module

Responsibilities

Site Ranking

Suitability Score

Land Analysis

Infrastructure Analysis

Environmental Constraints

---

## Database Module

Responsibilities

Store Users

Store Projects

Store Site Data

Store Predictions

Store Reports

---

## Reports Module

Responsibilities

Generate PDF Reports

Generate Excel Reports

Export Results

Site Assessment Reports

Investment Reports

---

## Dashboard Module

Responsibilities

Charts

Maps

Project Status

Predictions

Site Comparison

Analytics

---

## API Services

Responsibilities

Backend APIs

Frontend Integration

Database Communication

Prediction Services

Authentication APIs
