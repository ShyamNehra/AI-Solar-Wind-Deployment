# Database Schema & Relational Design Document

## 1. Overview
The database layer uses **SQLAlchemy 2.0 ORM** supporting **SQLite** (local development) and **PostgreSQL** (production deployment).

---

## 2. Relational Entity Relationship (ER) Diagram

```mermaid
erDiagram
    USERS ||--o{ PROJECTS : "creates"
    PROJECTS ||--o{ SITES : "contains"
    SITES ||--o{ SAVED_SITES : "persists"
    SITES ||--o{ RECENT_SITES : "records evaluation"
    SITES ||--o{ ENVIRONMENTAL_DATA : "has"
    SITES ||--o{ PREDICTIONS : "generates"
    SITES ||--o{ SUITABILITY_SCORES : "evaluates"

    USERS {
        int id PK
        string email UK
        string username UK
        string hashed_password
        string full_name
        string organization
        string organization_id
        string role
        boolean is_active
        datetime created_at
    }

    PROJECTS {
        int id PK
        string project_name
        string organization_id
        int created_by_id FK
        string region
        string project_type
        string status
        datetime created_at
    }

    SITES {
        int id PK
        int project_id FK
        string site_name
        float latitude
        float longitude
        string region
        float elevation_m
        string status
        datetime created_at
    }

    SAVED_SITES {
        int id PK
        string organization_id
        string name
        string description
        float latitude
        float longitude
        string status
        float score
        datetime created_at
    }

    RECENT_SITES {
        int id PK
        string organization_id
        string name
        float latitude
        float longitude
        string status
        string region
        string elevation
        string existing_infra
        float score
        string project_id
        string evaluated_by
        datetime created_at
    }

    ENVIRONMENTAL_DATA {
        int id PK
        int site_id FK
        float solar_ghi
        float wind_speed_100m
        float temperature_ambient
        float cloud_cover_pct
        datetime fetched_at
    }

    PREDICTIONS {
        int id PK
        int site_id FK
        float annual_yield_mwh
        float capacity_factor_pct
        float capex_inr
        float opex_inr
        float npv_25yr_inr
        float irr_pct
        float lcoe_inr
        datetime generated_at
    }

    SUITABILITY_SCORES {
        int id PK
        int site_id FK
        float overall_score
        float resource_score
        float terrain_score
        float infra_score
        float env_score
        float econ_score
        string final_status
    }
```

---

## 3. Detailed Data Dictionary

### 3.1 `users` Table
- `id` (INTEGER, Primary Key, Autoincrement)
- `email` (VARCHAR(120), Unique, Indexed, Not Null)
- `username` (VARCHAR(50), Unique, Indexed, Not Null)
- `hashed_password` (VARCHAR(255), Not Null)
- `full_name` (VARCHAR(100), Nullable)
- `organization` (VARCHAR(100), Nullable)
- `organization_id` (VARCHAR(50), Indexed, Default: "1001")
- `role` (VARCHAR(30), Default: "ENERGY_PLANNER")
- `is_active` (BOOLEAN, Default: True)
- `created_at` (TIMESTAMP, Default: UTC NOW)

### 3.2 `saved_sites` Table
- `id` (INTEGER, Primary Key, Autoincrement)
- `organization_id` (VARCHAR(50), Indexed, Not Null)
- `name` (VARCHAR(100), Not Null)
- `description` (VARCHAR(255), Nullable)
- `latitude` (FLOAT, Not Null)
- `longitude` (FLOAT, Not Null)
- `status` (VARCHAR(20), Not Null)
- `score` (FLOAT, Not Null)
- `created_at` (TIMESTAMP, Default: UTC NOW)

*Composite Index*: `idx_saved_sites_org_lat_lng` (`organization_id`, `latitude`, `longitude`) for fast workspace deduplication.

### 3.3 `recent_sites` Table
- `id` (INTEGER, Primary Key, Autoincrement)
- `organization_id` (VARCHAR(50), Indexed, Not Null)
- `name` (VARCHAR(200), Not Null)
- `latitude` (FLOAT, Not Null)
- `longitude` (FLOAT, Not Null)
- `status` (VARCHAR(50), Default: "EVALUATED")
- `region` (VARCHAR(100), Nullable)
- `elevation` (VARCHAR(100), Nullable)
- `existing_infra` (TEXT, Nullable)
- `score` (FLOAT, Nullable)
- `project_id` (VARCHAR(100), Nullable)
- `evaluated_by` (VARCHAR(100), Nullable)
- `created_at` (TIMESTAMP, Default: UTC NOW)

*Workspace History Index*: `idx_recent_sites_org_created` (`organization_id`, `created_at` DESC) for sub-millisecond team evaluation history retrieval.

---

## 4. Indexing Strategy & Spatial Optimizations

1. **Spatial Bounding Box Indexing**: Compound index on `(latitude, longitude)` enables sub-millisecond bounding box lookup for nearby sites.
2. **Workspace Isolation Indexing**: Index on `organization_id` enforces strict multi-tenant data isolation across workspace queries.