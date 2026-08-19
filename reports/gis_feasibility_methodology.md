# GIS Spatial Multi-Criteria Feasibility Methodology

## 1. Overview & Objective
This technical document outlines the spatial multi-criteria decision analysis (MCDA) and exclusion constraint logic implemented in the **AI Solar & Wind Deployment Intelligence Platform**.

The spatial evaluation engine determines site viability by applying **Hard Constraints** (binary pass/fail exclusion zones) and **Soft Suitability Weighting** across terrain, infrastructure, environmental, and financial criteria.

---

## 2. Hard Exclusion Constraints (Binary Cutoffs)

Any site location violating a single hard constraint is automatically marked as **REJECTED ZONE**.

| Constraint Layer | Buffer / Threshold Criteria | Data Source | Rationale |
| :--- | :--- | :--- | :--- |
| **Terrain Slope** | Slope $> 15.0^\circ$ | SRTM DEM (30m resolution) | Steep slopes increase civil construction costs, soil erosion risk, and shading. |
| **Water Bodies & Rivers** | $150\text{m}$ Buffer Distance | OSM Overpass / HydroSHEDS | Flood prevention, environmental protection, and soft soil instability. |
| **Protected Ecological Zones** | $500\text{m}$ Buffer Distance | WDPA / OpenStreetMap | National parks, wildlife sanctuaries, and biodiversity reserves. |
| **Urban & Residential Settlements** | $300\text{m}$ Buffer Distance | OpenStreetMap Land Use | Noise abatement (wind turbines) and glare/shadow flicker mitigation (solar). |
| **Military & Restricted Zones** | Binary Spatial Exclusion | National Geofence Layers | Radar interference and security airspace restrictions. |

---

## 3. Soft Suitability Scoring Model (0 - 100 Scale)

For viable sites passing all hard constraints, a normalized composite suitability score ($S$) is calculated:

$$S = w_r \cdot S_{\text{resource}} + w_g \cdot S_{\text{geo}} + w_i \cdot S_{\text{infra}} + w_e \cdot S_{\text{env}} + w_c \cdot S_{\text{econ}}$$

### Parameter Weights ($w_i$) & Scaling Curves

1. **Resource Potential ($w_r = 0.35$)**:
   - Solar GHI: Linear scaling from $3.5\text{ kWh/m}^2/\text{day}$ (0 pts) to $\ge 6.5\text{ kWh/m}^2/\text{day}$ (100 pts).
   - Wind Speed at 100m: Cubic power curve scaling from $3.0\text{ m/s}$ (0 pts) to $\ge 8.5\text{ m/s}$ (100 pts).

2. **Geographic & Slope Usability ($w_g = 0.20$)**:
   - Terrain Slope: $100 - (\text{slope} \times 6.0)$, capping at $0$ if slope $> 15^\circ$.

3. **Infrastructure Proximity ($w_i = 0.20$)**:
   - Distance to Power Grid Substation: Exponential decay curve favoring sites $< 5\text{ km}$.
   - Distance to Logistics Road: Linear penalty for distance $> 2\text{ km}$.

4. **Environmental Buffer Quality ($w_e = 0.10$)**:
   - Penalizes sites within $150\text{m} - 300\text{m}$ of water bodies or non-protected forests.

5. **Economic Feasibility ($w_c = 0.15$)**:
   - Mapped directly to estimated Return on Investment (ROI %).

---

## 4. Resilient Spatial API Failover Architecture

To guarantee high system availability during spatial data retrieval, the GIS pipeline executes a 3-tier mirror failover strategy:

```
                  ┌─────────────────────────────────────┐
                  │ 1. Primary Overpass OpenStreetMap   │
                  └──────────────────┬──────────────────┘
                                     │
                             (Timeout > 4.5s?)
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │ 2. Backup GIS Private Mirror Hub    │
                  └──────────────────┬──────────────────┘
                                     │
                             (Network Unreachable?)
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │ 3. Geofenced Synthetic Fallback Pass│
                  │ (Pushes GIS Advisory to Bell Notif) │
                  └─────────────────────────────────────┘
```

1. **Primary OSM Overpass Node**: Executes bounding box queries (`[out:json][timeout:5]`) for rivers, roads, and land use.
2. **Backup GIS Private Mirror**: Query automatically falls over to private secondary API mirrors if primary times out.
3. **Geofenced Advisory Fallback**: If network mirrors fail, the engine issues a `gis_unverified_pass` result and dynamically pushes a `"GIS API timeout: Manual inspection required"` warning alert strictly to the user's notification bell without breaking pipeline execution.
