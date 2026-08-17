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