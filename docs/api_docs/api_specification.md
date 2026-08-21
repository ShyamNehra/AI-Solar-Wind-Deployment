# REST API Technical Specification

## 1. Overview
This document provides the technical reference specification for the **AI Solar & Wind Deployment Intelligence REST API**.

- **Base URL**: `http://${window.location.hostname}:8000` (dynamically resolves hostname; overridden by `VITE_API_BASE_URL` in production)
- **API Version**: `1.0.0`
- **Protocol**: HTTP / HTTPS
- **Authentication**: JWT Bearer Token (`Authorization: Bearer <token>`)

---

## 2. Authentication & User Endpoints

### 2.1 User Login
- **Endpoint**: `POST /auth/login`
- **Rate Limit**: `5 requests / minute / IP`
- **Description**: Authenticates user credentials and returns JWT token.

#### Request Payload
```json
{
  "username_or_email": "shyam_nehra",
  "password": "password123",
  "organization_id": "1001"
}
```

#### Response (HTTP 200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "ADMINISTRATOR",
  "user_id": 1,
  "username": "shyam_nehra",
  "full_name": "Shyam Nehra",
  "organization": "Infosys Energy Intelligence",
  "organization_id": "1001"
}
```

---

### 2.2 User Registration
- **Endpoint**: `POST /auth/register`
- **Rate Limit**: `10 requests / minute / IP`
- **Description**: Registers a new user account under a team workspace.

#### Request Payload
```json
{
  "email": "user@energy.com",
  "username": "energy_user",
  "password": "Password@123",
  "full_name": "Energy Analyst",
  "organization": "New Energy Team",
  "organization_id": "1001",
  "workspace_mode": "join",
  "role": "ENERGY_PLANNER"
}
```

---

## 3. Predictions & Site Assessment Endpoints

### 3.1 Full Standardized Site Analysis
- **Endpoint**: `POST /predictions/full-analysis`
- **Rate Limit**: `20 requests / minute / IP`
- **Authentication**: Bearer Token Optional / Recommended

#### Request Payload
```json
{
  "latitude": 27.5397,
  "longitude": 71.9152,
  "technology": "SOLAR",
  "solar_capacity_mw": 50.0,
  "wind_capacity_mw": 0.0,
  "organization_id": "1001"
}
```

#### Response (HTTP 200 OK)
```json
{
  "status": "success",
  "data": {
    "technical_feasibility": {
      "site_name": "Bhadla Solar Corridor",
      "final_status": "APPROVED",
      "overall_suitability_score": 88.5,
      "land_type": "gis_verified",
      "terrain_slope_deg": 2.1,
      "solar_ghi_kwh_m2_day": 6.25,
      "wind_speed_100m_ms": 4.8
    },
    "energy_yield": {
      "annual_net_yield_mwh": 96360.0,
      "capacity_factor_pct": 22.0,
      "monthly_curve_mwh": [8100, 7900, 8400, 8900, 9200, 8800, 7500, 7200, 7600, 8100, 8300, 8400]
    },
    "financial_appraisal": {
      "total_capex_inr": 2250000000,
      "annual_opex_inr": 35000000,
      "annual_revenue_inr": 274626000,
      "npv_25yr_inr": 1845000000,
      "irr_pct": 14.8,
      "lcoe_inr_per_kwh": 2.15,
      "payback_years": 6.2,
      "roi_pct": 10.6
    }
  }
}
```

---

### 3.2 Machine Learning Forecast Execution
- **Endpoint**: `POST /predictions/forecast`
- **Rate Limit**: `20 requests / minute / IP`

---

## 4. Team Saved Sites Endpoints

### 4.1 Fetch Saved Workspace Sites
- **Endpoint**: `GET /sites/saved?organization_id=1001`
- **Authentication**: `Required (Bearer JWT)`

#### Response (HTTP 200 OK)
```json
[
  {
    "id": 1,
    "organization_id": "1001",
    "name": "Bhadla Solar Park Phase I",
    "description": "High GHI solar candidate parcel",
    "latitude": 27.5397,
    "longitude": 71.9152,
    "status": "APPROVED",
    "score": 88.5,
    "created_at": "2026-08-19T12:00:00Z"
  }
]
```

### 4.2 Save Workspace Favorite Site
- **Endpoint**: `POST /sites/saved`
- **Authentication**: `Required (Bearer JWT)`

---

## 5. Team Recent Search History Endpoints

### 5.1 Fetch Recent Workspace Evaluations
- **Endpoint**: `GET /sites/recent?organization_id=1001`
- **Authentication**: `Required (Bearer JWT)`
- **Description**: Returns the 10 most recent site evaluations conducted across all team members in the specified workspace.

#### Response (HTTP 200 OK)
```json
[
  {
    "id": 1,
    "organization_id": "1001",
    "name": "Bhadla Solar Park",
    "latitude": 27.5397,
    "longitude": 71.9152,
    "status": "APPROVED",
    "region": "Western Region",
    "elevation": "220 Meters",
    "existing_infra": "Substation adjacent, Road access clear",
    "score": 94.8,
    "project_id": "PRJ-INFOSYS-01",
    "evaluated_by": "shyam_nehra",
    "created_at": "2026-08-21T20:48:00Z"
  }
]
```

### 5.2 Record Recent Workspace Evaluation
- **Endpoint**: `POST /sites/recent`
- **Authentication**: `Required (Bearer JWT)`
- **Description**: Records or updates a recent site evaluation for the team workspace.

---

## 6. HTTP Error Payloads & Status Codes

| Code | Status | Cause | Payload Example |
| :--- | :--- | :--- | :--- |
| `401` | Unauthorized | Missing or expired JWT token | `{"detail": "Not authenticated"}` |
| `400` | Bad Request | Invalid coordinates or parameters | `{"detail": "Latitude must be between -90 and +90."}` |
| `429` | Too Many Requests | Rate limit threshold exceeded | `{"detail": "Rate limit exceeded: 5 per 1 minute"}` |
| `500` | Internal Server Error | Global unhandled exception | `{"detail": "An internal server error occurred. Request logged for safety compliance."}` |
