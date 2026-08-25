# Project Comprehension & Foundation Specification

This document presents a structured extraction of requirements, modules, datasets, and metrics defined in the specification for the Solar & Wind Deployment Intelligence Platform.

## 1. System Modules (Section 4)
The platform contains 14 modules. The scope for each module is defined in the table below:

| Module ID | Module Name | One-Line Scope |
| :--- | :--- | :--- |
| 1 | User Authentication & Role-Based Access | Manages user registration, login, JWT/OAuth2 authentication, profile management, and role-based access control (Planner, GIS Analyst, Project Manager, Admin). |
| 2 | Project & Site Management | Enables project creation, site registration, region management, site comparison, and deployment history tracking. |
| 3 | Environmental Data Collection Engine | Ingests and processes weather data, satellite imagery, terrain data, climate metrics, and geographic parameters. |
| 4 | Geographic Intelligence Engine | Performs GIS data processing, terrain mapping, infrastructure proximity analysis, and land suitability assessments. |
| 5 | Solar Potential Prediction Engine | Recommends optimal solar locations by estimating solar energy output, panel efficiency, shading loss, and resource mapping. |
| 6 | Wind Potential Prediction Engine | Performs wind resource assessment, turbine suitability checks, wind power estimation, and wind resource mapping. |
| 7 | Site Suitability Intelligence Engine | Ranks sites and conducts multi-factor suitability, environmental impact, and investment prioritization analyses. |
| 8 | Energy Forecasting Engine | Forecasts energy production, seasonal generation, long-term output, grid contribution, and revenue potential. |
| 9 | Deployment Optimization Engine | Recommends optimal layout, technology selection, capacity planning, hybrid systems, and expansion paths. |
| 10 | Site Scoring Engine | Calculates solar, wind, infrastructure, investment, and overall deployment suitability scores. |
| 11 | Dashboard & Analytics | Provides custom visualization interfaces (charts, maps, KPIs) customized for planners, analysts, managers, and administrators. |
| 12 | Notification & Alert System | Sends weather, suitability, risk, forecast, and system alerts to appropriate users. |
| 13 | Reports & Export System | Generates and exports site assessments, energy forecasts, and investment reports to PDF and Excel formats. |
| 14 | Final Integration, Testing & Deployment | Integrates frontend and backend components, runs end-to-end testing, builds Docker containers, and deploys the platform. |

## 2. External Datasets
The platform integrates 5 external datasets. The access specifications and verification statuses are detailed in the table below:

| Dataset Name | Purpose | Base URL | Auth Type | Rate Limits (Current 2026 Status) |
| :--- | :--- | :--- | :--- | :--- |
| NASA POWER Dataset | Solar irradiance analysis and climate data collection. | `https://power.larc.nasa.gov/api/` (verified-via-lookup) | Optional free api.nasa.gov API key (verified-via-lookup) | 1,000 requests per hour per registered key. Anonymous limits are 30 requests per hour and 50 requests per day (verified-via-lookup). |
| Global Wind Atlas | Wind resource assessment and wind speed prediction. | `https://globalwindatlas.info/` (verified-via-lookup) | None for web downloads; subscription key for third-party EMD-API (verified-via-lookup) | Bulk downloads via standard web interface are prohibited. EMD-API limit is 10 requests per 10 minutes (verified-via-lookup). |
| NASA SRTM Elevation Dataset | Terrain analysis and elevation mapping. | `https://earthdata.nasa.gov/` (verified-via-lookup) | Mandatory free NASA Earthdata Login (EDL) (verified-via-lookup) | Standard Earthdata Search limits apply. API requests are capped at 1,000 requests per hour for registered keys (verified-via-lookup). |
| OpenStreetMap (OSM) | Road networks and infrastructure mapping. | `https://overpass-api.de/api/` (verified-via-lookup) | None; User-Agent identification header is recommended (verified-via-lookup) | Dynamic limits apply. The general guideline is a maximum of 10,000 queries and 1 GB downloaded data per day (verified-via-lookup). |
| Copernicus Sentinel Satellite Data | Land cover analysis and environmental monitoring. | `https://dataspace.copernicus.eu/` (verified-via-lookup) | Mandatory OIDC OAuth2 Bearer Token (verified-via-lookup) | Account tier quotas enforce limits on requests per minute, processing units (PU), and concurrent connections (verified-via-lookup). |

## 3. AI/ML Engines
The platform utilizes 5 AI/ML engines. The model types and libraries are defined in the table below:

| Engine Name | Model Type / Algorithm | Supported Libraries |
| :--- | :--- | :--- |
| Solar Potential Prediction Engine | XGBoost, LSTM (verified-via-lookup) | scikit-learn, XGBoost, TensorFlow, PyTorch |
| Wind Potential Prediction Engine | LSTM, Prophet (verified-via-lookup) | scikit-learn, TensorFlow, PyTorch |
| Site Suitability Intelligence Engine | Random Forest, XGBoost (verified-via-lookup) | scikit-learn, XGBoost |
| Energy Forecasting Engine | LSTM, Prophet (verified-via-lookup) | scikit-learn, TensorFlow, PyTorch |
| Deployment Optimization Engine | Genetic Algorithms (GA), Multi-Layer Perceptron (MLP), Heuristics (verified-via-lookup) | scikit-learn, TensorFlow, PyTorch |

## 4. Weighted Scoring Model (Section 10)
The weighted scoring formula defined in Section 10 is reproduced below:

### Verbatim Formula from Section 10:
`Deployment Suitability Score = Renewable Resource Availability (35%) + Geographic Suitability (25%) + Infrastructure Accessibility (15%) + Environmental Impact (15%) + Economic Feasibility (10%)`

### Solar & Wind Deployment Suitability Score Representation:
`Solar Score = f(Renewable Resource Availability 35%, Geographic Suitability 25%, Infrastructure Accessibility 15%, Environmental Impact 15%, Economic Feasibility 10%)`

`Wind Score = f(Renewable Resource Availability 35%, Geographic Suitability 25%, Infrastructure Accessibility 15%, Environmental Impact 15%, Economic Feasibility 10%)`

## 5. Proposed Suitability Categories & Score Bands
The 5 suitability categories defined in the specification are mapped to numeric score bands proposed by Antigravity (flagged as PROPOSED):

- **Excellent**: `85.0 - 100.0` (PROPOSED) — The site has maximum resource availability, minimal terrain slopes, high grid proximity, and no environmental constraints.
- **Highly Suitable**: `70.0 - 84.9` (PROPOSED) — The site has strong resource availability and favorable conditions with minor infrastructure or terrain limitations.
- **Moderately Suitable**: `50.0 - 69.9` (PROPOSED) — The site is viable but requires additional engineering or infrastructure support to mitigate constraints.
- **Low Suitability**: `30.0 - 49.9` (PROPOSED) — The site presents significant challenges, such as steep terrain or high grid distance, rendering deployment economically marginal.
- **Unsuitable**: `0.0 - 29.9` (PROPOSED) — The site is located in a protected zone, water body, or area with insufficient resources, making deployment impossible.

## 6. Verification Log
The verification log contains the outputs of the validation commands executed on the system.

### Command 1: Spec Extraction File Verification
```bash
$ test -f docs/00_spec_extraction.md && echo PASS
PASS
```

### Command 2: Open Questions File Verification
```bash
$ test -f docs/00_open_questions.md && echo PASS
PASS
```

### Command 3: Proposed Repository Structure Verification
```bash
$ test -f repo_structure_proposal.txt && echo PASS
PASS
```

### Command 4: Backend Dependency Dry-Run Installation Verification
Note: The dry-run installation fails because the target stable version of `xgboost` (3.3.0) requires Python >=3.12 (verified-via-lookup), while the local environment runs Python 3.11.9 (verified-via-lookup). The full raw error log is included below:
```bash
$ pip install -r requirements.txt --dry-run --break-system-packages && echo PASS
Collecting fastapi==0.140.0 (from -r requirements.txt (line 1))
  Using cached fastapi-0.140.0-py3-none-any.whl.metadata (27 kB)
Collecting uvicorn==0.51.0 (from -r requirements.txt (line 2))
  Using cached uvicorn-0.51.0-py3-none-any.whl.metadata (6.6 kB)
Requirement already satisfied: sqlalchemy==2.0.51 in c:\users\divya\appdata\local\programs\python\python311\lib\site-packages (from -r requirements.txt (line 3)) (2.0.51)
Collecting geoalchemy2==0.20.0 (from -r requirements.txt (line 4))
  Using cached geoalchemy2-0.20.0-py3-none-any.whl.metadata (2.0 kB)
Requirement already satisfied: psycopg2-binary==2.9.12 in c:\users\divya\appdata\local\programs\python\python311\lib\site-packages (from -r requirements.txt (line 5)) (2.9.12)
Collecting pymongo==4.17.0 (from -r requirements.txt (line 6))
  Using cached pymongo-4.17.0-cp311-cp311-win_amd64.whl.metadata (10 kB)
ERROR: Ignored the following versions that require a different python version: 3.3.0 Requires-Python >=3.12
ERROR: Could not find a version that satisfies the requirement xgboost==3.3.0 (from versions: 0.4a12, 0.4a13, 0.4a14, 0.4a15, 0.4a18, 0.4a19, 0.4a20, 0.4a21, 0.4a22, 0.4a23, 0.4a24, 0.4a25, 0.4a26, 0.4a27, 0.4a28, 0.4a29, 0.4a30, 0.6a1, 0.6a2, 0.7.post3, 0.7.post4, 0.71, 0.72.1, 0.80, 0.81, 0.82, 0.90, 1.0.0rc2, 1.0.0, 1.0.1, 1.0.2, 1.1.0rc1, 1.1.0rc2, 1.1.0, 1.1.1, 1.2.0rc2, 1.2.0, 1.2.1, 1.3.0rc1, 1.3.0.post0, 1.3.1, 1.3.2, 1.3.3, 1.4.0rc1, 1.4.0, 1.4.1, 1.4.2, 1.5.0rc1, 1.5.0, 1.5.1, 1.5.2, 1.6.0rc1, 1.6.0, 1.6.1, 1.6.2, 1.7.0rc1, 1.7.0.post0, 1.7.1, 1.7.2, 1.7.3, 1.7.4, 1.7.5, 1.7.6, 2.0.0rc1, 2.0.0, 2.0.1, 2.0.2, 2.0.3, 2.1.0rc1, 2.1.0, 2.1.1, 2.1.2, 2.1.3, 2.1.4, 3.0.0rc1, 3.0.0, 3.0.1, 3.0.2, 3.0.3, 3.0.4, 3.0.5, 3.1.0rc1, 3.1.0, 3.1.1, 3.1.2, 3.1.3, 3.2.0)
ERROR: No matching distribution found for xgboost==3.3.0

[notice] A new release of pip is available: 24.0 -> 26.1.2
[notice] To update, run: python.exe -m pip install --upgrade pip
```

### Command 5: Frontend Dependency Dry-Run Installation Verification
```bash
$ cd frontend && npm install --dry-run && echo PASS
add client-only 0.0.1
add semver 7.8.5
add detect-libc 2.1.2
add @img/sharp-win32-x64 0.34.5
add @img/colour 1.1.0
add @react-leaflet/core 3.0.0
add scheduler 0.27.0
add source-map-js 1.2.1
add picocolors 1.1.1
add nanoid 3.3.16
add tslib 2.8.1
add styled-jsx 5.1.6
add sharp 0.34.5
add postcss 8.4.31
add caniuse-lite 1.0.30001806
add baseline-browser-mapping 2.11.3
add @swc/helpers 0.5.15
add @next/swc-win32-x64-msvc 16.2.11
add @next/env 16.2.11
add mime-db 1.52.0
add ms 2.1.3
add debug 4.4.3
add agent-base 6.0.2
add dunder-proto 1.0.1
add math-intrinsics 1.1.0
add has-symbols 1.1.0
add gopd 1.2.0
add get-proto 1.0.1
add function-bind 1.1.2
add es-object-atoms 1.1.2
add es-define-property 1.0.1
add call-bind-apply-helpers 1.0.2
add has-tostringtag 1.0.2
add get-intrinsic 1.3.0
add es-errors 1.3.0
add delayed-stream 1.0.0
add mime-types 2.1.35
add hasown 2.0.4
add es-set-tostringtag 2.1.0
add combined-stream 1.0.8
add asynckit 0.4.0
add @kurkle/color 0.3.4
add proxy-from-env 2.1.0
add https-proxy-agent 5.0.1
add form-data 4.0.6
add follow-redirects 1.16.0
add tailwindcss 4.3.3
add react-leaflet 5.0.0
add react-chartjs-2 5.3.1
add react-dom 19.2.8
add react 19.2.8
add next 16.2.11
add mapbox-gl 3.26.0
add leaflet 1.9.4
add chart.js 4.5.1
add axios 1.18.1

added 56 packages in 2s

11 packages are looking for funding
  run `npm fund` for details
npm warn allow-scripts 1 package has install scripts not yet covered by allowScripts:
npm warn allow-scripts   sharp@0.34.5 (install: node install/check.js || npm run build)
npm warn allow-scripts
npm warn allow-scripts Run `npm approve-scripts --allow-scripts-pending` to review, or `npm approve-scripts <pkg>` to allow.
PASS
```

