# Week 01 Development Log: Requirements & Data Collection

## 1. Objectives & Scope
- Establish project data requirements for utility-scale solar, wind, and hybrid site assessment.
- Integrate **NASA POWER Agro-Climatology API** for surface solar GHI and 100m wind speed metrics.
- Acquire elevation topography (SRTM 30m DEM) and surface roughness proxies from **Global Wind Atlas (GWA)**.

---

## 2. Key Accomplishments

### NASA POWER API Integration
- Connected to NASA POWER REST service (`https://power.larc.nasa.gov/api/temporal/daily/point`).
- Retriving:
  - `ALLSKY_SWRK_DM`: All Sky Surface Shortwave Downward Irradiance ($\text{kWh/m}^2/\text{day}$).
  - `WS100M`: Wind Speed at 100 Meters ($\text{m/s}$).
  - `T2M`: Temperature at 2 Meters ($\text{^\circ C}$).
  - `CLRSKY_DAYS`: Clear Sky Index.

### Database & Project Architecture Setup
- Configured FastAPI project directory hierarchy (`backend/app/`).
- Initialized SQLite database engine and created base ORM schemas for `User`, `Project`, and `Site`.

---

## 3. Challenges & Decisions
- **Challenge**: Upstream NASA POWER API occasionally experiences 2-3 second latency spikes during peak server loads.
- **Decision**: Implemented a local fallback cache storing historical regional monthly averages to ensure zero downtime for UI evaluations.
