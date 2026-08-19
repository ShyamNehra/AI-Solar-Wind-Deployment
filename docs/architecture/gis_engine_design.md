# GIS Engine Design & Failover Architecture

## 1. Overview
The GIS & Spatial Exclusion Engine provides real-time spatial constraint screening (river buffers, protected forest boundaries, slope thresholds) for candidate solar and wind deployment sites.

---

## 2. Multi-Mirror Overpass Failover Architecture

To maintain high system availability during spatial queries across public GIS networks, the engine implements a **3-tier failover cluster**:

```
                  ┌──────────────────────────────────────────┐
                  │ 1. Primary Overpass OSM Node (Main)      │
                  │    https://overpass-api.de/api/interpreter│
                  └────────────────────┬─────────────────────┘
                                       │
                             (Timeout > 4.5s?)
                                       │
                                       ▼
                  ┌──────────────────────────────────────────┐
                  │ 2. Secondary Overpass Mirror (Backup)    │
                  │    https://overpass.kumi.systems/api/    │
                  └────────────────────┬─────────────────────┘
                                       │
                             (Network Unreachable?)
                                       │
                                       ▼
                  ┌──────────────────────────────────────────┐
                  │ 3. Geofenced Synthetic Advisory Fallback │
                  │    Pushes 'gis_unverified_pass' warning  │
                  │    alert strictly to Bell Dropdown Menu  │
                  └──────────────────────────────────────────┘
```

---

## 3. Spatial Caching & Precision Indexing

- **Spatial Precision Grid**: Coordinates are truncated to 3 decimal places ($\sim 110\text{m}$ grid precision) for spatial query caching.
- **In-Memory Cache Layer**: LRU cache stores spatial Overpass bounding box results for 1 hour to reduce upstream API load.
- **Buffer Geometry Calculation**: Uses Shapely planar buffer approximations:
  - $150\text{m}$ River Buffer $\approx 0.00135^\circ$ planar offset.
  - $300\text{m}$ Settlement Buffer $\approx 0.00270^\circ$ planar offset.
  - $500\text{m}$ Sanctuary Buffer $\approx 0.00450^\circ$ planar offset.

---

## 4. Offshore & Geofence Boundary Matrix

- Coordinates located outside territorial land boundaries or inside designated offshore marine zones are flagged as **`OFFSHORE_WIND_ZONE`** or **`EXCLUSIVE_ECONOMIC_ZONE`**, switching evaluation rules from land slope to bathymetry water depth ($<40\text{m}$ fixed foundation vs. $>40\text{m}$ floating wind turbines).
