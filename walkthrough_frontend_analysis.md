# Frontend Analysis Screen Walkthrough

This document covers the implementation, structure, and usage of the Site Analysis Screen in the Solar & Wind Deployment Intelligence Platform.

---

## 1. Frontend Structure & Files

### Files Created
1. **[app/static/js/analysis.js](file:///c:/Users/kanda/OneDrive/Documents/solar-wind-intelligence-api/AI-Solar-Wind-Deployment/app/static/js/analysis.js)**:
   - Contains the centralized API client. Encapsulates HTTP request composition, JSON payload serialization, and network/HTTP/Pydantic validation error handling.
2. **[walkthrough_frontend_analysis.md](file:///c:/Users/kanda/OneDrive/Documents/solar-wind-intelligence-api/AI-Solar-Wind-Deployment/walkthrough_frontend_analysis.md)**:
   - This documentation file.

### Files Modified
1. **[app/templates/index.html](file:///c:/Users/kanda/OneDrive/Documents/solar-wind-intelligence-api/AI-Solar-Wind-Deployment/app/templates/index.html)**:
   - Standardized to load Leaflet and the centralized API script in `<head>`.
   - Integrated the "Site Analysis" sidebar navigation button and the tab container layout (`tab-analysis`).
   - Added map initialization, dynamic layout state controller (loading, success, error, placeholder), and form submission handlers.

---

## 2. API Integration & Payload Mapping

The centralized client function is defined as:
```javascript
async function analyzeSite(latitude, longitude, configuration)
```
- **Endpoint**: `POST /analysis` (relative path resolves to host automatically, easing Docker/production deployments).
- **Request Format**: Serialized JSON matching the backend's `AnalysisRequest` schema:
  ```json
  {
    "project_name": "Ad-hoc Site Analysis",
    "location": "Analysis: 19.8135, 85.8312",
    "latitude": 19.8135,
    "longitude": 85.8312,
    "installed_capacity_kw": 1000.0,
    "solar_system_efficiency": 0.80,
    "wind_operational_losses": 0.15,
    "electricity_tariff_inr_per_kwh": 7.0,
    "cost_per_kw": 25000.0,
    "additional_installation_percentage": 10.0,
    "elevation": 10.0,
    "slope": 2.0,
    "distance_to_road": 1.5,
    "distance_to_grid": 3.5
  }
  ```

---

## 3. Frontend Application States

### A. Placeholder State
* Displays a compass icon and prompts the user to enter coordinate targets.

### B. Loading State
* Triggered upon form submit.
* Disables the "Analyse Site" button to prevent duplicate clicks.
* Shows a bouncing loading pulse indicator and messages explaining pipeline steps.

### C. Success State
* Triggered on `HTTP 200`.
* Renders the Leaflet map with a marker centered at the analyzed location.
* Populates organized cards showing:
  - **Site Designation**: Location name and coordinates.
  - **Recommended Strategy**: Technology choice badge, confidence rating, and engineering feasibility.
  - **Technical Feasibility**: Soft feasibility score, violation counts, and details of critical constraint violations.
  - **Suitability Scores**: Individual resource, terrain, grid connection, environmental, and economic score parameters.
  - **Estimated Energy**: Comparative solar, wind, hybrid, and recommended annual generation yields (kWh).
  - **Financial Planning**: CapEx project cost, annual revenue, simple payback period (years), and ROI (%).
  - **ML Explainability**: Decision reasons, top 3 feature importances, and text description.

### D. Error Handling
* Parses response errors:
  - Coordinate bounds ($>90$, $<-90$, $>180$, $<-180$) trigger user-friendly coordinate format warnings.
  - Pydantic/FastAPI validation exceptions (e.g. `HTTP 422`) are parsed and rendered cleanly as sentences.
  - Network connection failures (server offline) display a fallback notification: *"Unable to connect to the analysis server. Please make sure the backend is running."*

---

## 4. Leaflet Map Integration
* A Leaflet instance is initialized on `DOMContentLoaded`.
* Upon a successful analysis run, the map centers on the selected coordinates, and a marker is created/updated with a popup listing the project name and location.
* Invaliding map size (`analysisMap.invalidateSize()`) is hooked into the tab switching routine, resolving container layout distortions when the tab is revealed.

---

## 5. How to Run the Platform

### Start Backend
```powershell
py -3.12 -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### Access Frontend
Open the following URL in your browser:
```
http://127.0.0.1:8000/dashboard
```
Navigate to the **Site Analysis** tab in the sidebar menu.
