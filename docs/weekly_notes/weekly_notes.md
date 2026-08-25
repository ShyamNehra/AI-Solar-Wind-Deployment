# Weekly Notes - Week 1

## What I Learned
- Understood the core requirements of the Solar Wind Deployment Intelligence project.
- Learned about various geographic and meteorological datasets essential for hybrid solar-wind energy site selection.
- Worked with API integrations: NASA POWER API for weather data and Overpass API for OpenStreetMap spatial query retrieval.
- Learned how to process GeoTIFF files and generate realistic spatial models (wind speed Weibull profiles and elevation matrices).
- Gained experience with FastAPI, ASGI server configurations (Uvicorn), and defining route controllers.
- Studied relational database architecture, SQL primary keys, foreign keys, and multi-table mapping for site analysis metadata.

## Datasets Explored
We have successfully downloaded and prepared five sample datasets:

1. **NASA POWER** (`datasets/nasa_power/nasa_power_bangalore.csv`):
   - **Contains**: Solar irradiance (`ALLSKY_SFC_SW_DWN`), Temperature (`T2M`), and Wind Speed (`WS2M`).
   - **Used For**: Solar and meteorological prediction.
   - **Properties**: 31 rows, 6 columns, 0 missing values.

2. **Global Wind Atlas** (`datasets/global_wind_atlas/wind_speed_bangalore.csv`):
   - **Contains**: Wind speed profiles at heights of 10m, 50m, and 100m.
   - **Used For**: Wind speed energy yield prediction.
   - **Properties**: 744 rows (hourly data for a month), 6 columns, 0 missing values.

3. **Sentinel-2** (`datasets/sentinel/sentinel2_sample.tif`):
   - **Contains**: Multi-spectral satellite band imagery.
   - **Used For**: Land cover classification and site constraint checking.
   - **Properties**: Standard GeoTIFF format (~1.7 MB).

4. **OpenStreetMap** (`datasets/openstreetmap/osm_infrastructure.json`):
   - **Contains**: Road networks, buildings, substations, and local infrastructure nodes.
   - **Used For**: Proximity analysis to transmission grids and transportation.
   - **Properties**: JSON format containing 7,025 features/elements.

5. **SRTM** (`datasets/srtm/elevation_bangalore.csv`):
   - **Contains**: Grid terrain elevation profiles.
   - **Used For**: Slope and aspect analysis for site suitability.
   - **Properties**: 10,000 rows (100x100 grid), 3 columns (`latitude`, `longitude`, `elevation_m`).

See detailed statistics in the [dataset_summary.md](file:///Users/priyadharshini/Desktop/infosys/solar-wind-deployment-intelligence/datasets/dataset_summary.md).

## Folder Structure Created
We established the standard mono-repo architecture:
- `backend/`: FastAPI skeleton with modules (`api/`, `auth/`, `database/`, `models/`, `schemas/`, `services/`, `utils/`) and automated `tests/` directory and `.env` configuration.
- `frontend/`: React + Vite client-side code structure with `src/components/`, `src/pages/`, `src/services/`, and `src/assets/`.
- `datasets/`: Separate subfolders for the five meteorological and spatial data layers.
- `docs/`: Design and architectural documentation folders including `docs/architecture/` and `docs/database_design/`.

## Design Artifacts Generated
- **Project Architecture Diagram**: Documented the multi-tier flow from UI to Gateway, core logic, and database caches. (See [architecture_design.md](file:///Users/priyadharshini/Desktop/infosys/solar-wind-deployment-intelligence/docs/architecture/architecture_design.md))
- **Database Design Draft**: Configured tables for Users, Projects, Sites, EnvironmentalData, SolarPrediction, WindPrediction, SuitabilityScore, and Reports. (See [database_design.md](file:///Users/priyadharshini/Desktop/infosys/solar-wind-deployment-intelligence/docs/database_design/database_design.md))
- **Module Responsibility Mapping**: Assigned clear inputs, boundaries, and outputs for all system components. (See [module_mapping.md](file:///Users/priyadharshini/Desktop/infosys/solar-wind-deployment-intelligence/docs/module_mapping.md))

## Backend API Endpoints Implemented
We implemented and tested GET routes using FastAPI:
- `GET /`: Welcome message
- `GET /health`: System status confirmation (`{"status": "Running"}`)
- `GET /about`: Project details (`{"project": "Solar & Wind Deployment Intelligence Platform"}`)

## Problems Faced
- **API Rate Limiting & Blocking**: Overpass API returned a `406 Not Acceptable` error when queried using python-requests without explicit headers. Fixed by supplying proper `Accept: application/json` headers and executing the query using standard `curl`.
- **Sentinel-2 Sample Links**: Multiple historical test repository links were deprecated or moved. Fixed by sourcing a clean test GeoTIFF from the official Rasterio GitHub repository.

## Next Goals
- Hook database connections to PostgreSQL using SQLAlchemy or SQLModel.
- Connect dataset parsers to ingest NASA, OSM, and SRTM CSVs/JSON into database tables.

---

# Weekly Notes - Week 2 (Milestones 3 & 4)

## What I Learned
- Implemented parameter normalization equations (Min-Max) for comparative scaling.
- Configured Random Forest Regressor models for solar GHI prediction.
- Designed and validated hard constraints (slope, elevation limits) and soft proximity weights (road, grid distance indices).
- Calculated industrial capacity yields and project payback matrices (ROI, project cost curves, tariff models).
- Experienced Docker containerization configurations for portable backend & frontend microservices.
- Created interactive mapping logic in React using the Leaflet library.

## Features Implemented
1. **Multi-Criteria Scoring Engine**: Normalizes and evaluates sites across Resource, Terrain, and Infrastructure indices.
2. **ML Solar Radiation Baseline**: Trains a Random Forest Regressor on the NASA POWER Bangalore CSV to forecast solar outputs, yielding feature importances (month, day, temp, wind).
3. **Capacity & Expansion Planning**: Computes deployment capacity (MW) and future expansion potential (Expandable, Limited, Not Expandable).
4. **Project Financial Model**: Evaluates investment cost, annual revenue, payback periods, and ROI.
5. **Unified API Gateway**: Exposes a unified `POST /api/analysis` endpoint that runs the entire end-to-end site analysis pipeline.
6. **Docker Configuration**: Added [Dockerfile.backend](file:///Users/priyadharshini/Desktop/infosys/solar-wind-deployment-intelligence/docker/Dockerfile.backend), [Dockerfile.frontend](file:///Users/priyadharshini/Desktop/infosys/solar-wind-deployment-intelligence/docker/Dockerfile.frontend), and updated [docker-compose.yml](file:///Users/priyadharshini/Desktop/infosys/solar-wind-deployment-intelligence/docker-compose.yml).
7. **Frontend Interactive Dashboard**: Built a dark-themed user console displaying full site assessments side-by-side with an OpenStreetMap locator map.


