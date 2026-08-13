import React, { useState, useEffect } from 'react';
import { runSiteAnalysis } from './services/analysis';
import { MapContainer, TileLayer, Marker, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix leaflet marker icons package issue in Webpack/Vite
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

// Helper component to center map on new coordinates
function ChangeView({ center }) {
  const map = useMap();
  map.setView(center, 13);
  return null;
}

function App() {
  // Input fields state
  const [lat, setLat] = useState(12.9716);
  const [lon, setLon] = useState(77.5946);
  const [area, setArea] = useState(80000);
  const [tariff, setTariff] = useState(5.5);
  const [slope, setSlope] = useState(2.5);
  const [elevation, setElevation] = useState(920);
  const [distGrid, setDistGrid] = useState(1200);
  const [distRoad, setDistRoad] = useState(400);

  // App lifecycle states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [mapCenter, setMapCenter] = useState([12.9716, 77.5946]);

  // Sync map center to coordinates
  const handleMapClick = (e) => {
    // If the map allows selection (optional future extension)
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    const payload = {
      latitude: parseFloat(lat),
      longitude: parseFloat(lon),
      area_sq_m: parseFloat(area),
      electricity_tariff_inr_kwh: parseFloat(tariff),
      slope_deg: parseFloat(slope),
      elevation_m: parseFloat(elevation),
      dist_grid_m: parseFloat(distGrid),
      dist_road_m: parseFloat(distRoad)
    };

    try {
      const data = await runSiteAnalysis(payload);
      setResult(data);
      setMapCenter([payload.latitude, payload.longitude]);
    } catch (err) {
      setError(err.message || "Failed to contact backend API. Make sure FastAPI server is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="navbar">
        <div className="brand">
          <span className="logo-icon">⚡</span>
          <h2>Solar & Wind Deployment Intelligence</h2>
        </div>
        <div className="status-badge">Milestone 4 Stable</div>
      </header>

      <main className="dashboard-grid">
        {/* Left Side: Parameters Input Form */}
        <section className="card form-card">
          <h3>Target Site Parameters</h3>
          <form onSubmit={handleAnalyze} className="inputs-form">
            <div className="input-group">
              <label>Latitude</label>
              <input 
                type="number" step="0.0001" min="-90" max="90" required
                value={lat} onChange={(e) => setLat(e.target.value)} 
              />
            </div>
            <div className="input-group">
              <label>Longitude</label>
              <input 
                type="number" step="0.0001" min="-180" max="180" required
                value={lon} onChange={(e) => setLon(e.target.value)} 
              />
            </div>
            <div className="input-group">
              <label>Land Area (sq meters)</label>
              <input 
                type="number" min="1" required
                value={area} onChange={(e) => setArea(e.target.value)} 
              />
            </div>
            <div className="input-group">
              <label>Tariff (₹ / kWh)</label>
              <input 
                type="number" step="0.1" min="0.1" required
                value={tariff} onChange={(e) => setTariff(e.target.value)} 
              />
            </div>

            <h4 className="section-divider">Physical Constraints</h4>
            
            <div className="input-grid-2">
              <div className="input-group">
                <label>Slope (degrees)</label>
                <input 
                  type="number" step="0.1" min="0" max="90" required
                  value={slope} onChange={(e) => setSlope(e.target.value)} 
                />
              </div>
              <div className="input-group">
                <label>Elevation (meters)</label>
                <input 
                  type="number" required
                  value={elevation} onChange={(e) => setElevation(e.target.value)} 
                />
              </div>
            </div>

            <div className="input-grid-2">
              <div className="input-group">
                <label>Dist to Grid (meters)</label>
                <input 
                  type="number" min="0" required
                  value={distGrid} onChange={(e) => setDistGrid(e.target.value)} 
                />
              </div>
              <div className="input-group">
                <label>Dist to Road (meters)</label>
                <input 
                  type="number" min="0" required
                  value={distRoad} onChange={(e) => setDistRoad(e.target.value)} 
                />
              </div>
            </div>

            <button type="submit" disabled={loading} className="btn btn-primary">
              {loading ? "Analyzing site..." : "📊 Analyze Site"}
            </button>
          </form>
        </section>

        {/* Right Side: Interactive Map View */}
        <section className="card map-card">
          <h3>Geographic Map View</h3>
          <div className="map-wrapper">
            <MapContainer center={mapCenter} zoom={13} style={{ height: "100%", width: "100%" }}>
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <Marker position={mapCenter} />
              <ChangeView center={mapCenter} />
            </MapContainer>
          </div>
          <div className="coordinates-overlay">
            Selected: Lat {lat}, Lon {lon}
          </div>
        </section>
      </main>

      {/* States Indicator */}
      {loading && (
        <div className="state-panel loading-state">
          <div className="spinner"></div>
          <p>Analyzing coordinates, computing suitability scoring, and querying prediction models...</p>
        </div>
      )}

      {error && (
        <div className="state-panel error-state">
          <h4>⚠️ Pipeline Execution Error</h4>
          <p>{error}</p>
        </div>
      )}

      {/* Results Section */}
      {result && (
        <section className="results-container animate-fade-in">
          <div className="results-header">
            <h3>Analysis Results for Candidate Site</h3>
            <div className={`feasibility-pill ${result.technical_assessment.technical_feasibility ? 'pill-green' : 'pill-red'}`}>
              {result.technical_assessment.technical_feasibility ? "🟢 Technically Feasible" : "❌ Rejected (Constraint Fail)"}
            </div>
          </div>

          <div className="results-grid">
            {/* Suitability Index */}
            <article className="card suitability-card">
              <h4>Site Suitability Index</h4>
              <div className="score-badge">
                <span className="score-num">{result.scoring.overall_suitability_score}</span>
                <span className="score-max">/100</span>
              </div>
              <p>Recommended Technology: <strong>{result.technical_assessment.recommended_deployment}</strong></p>
              <p className="remarks">{result.technical_assessment.remarks}</p>
            </article>

            {/* Category breakdown */}
            <article className="card scores-card">
              <h4>Scoring Index Categories</h4>
              <ul className="category-list">
                <li>
                  <span>Renewable Potential</span>
                  <div className="progress-bar-container">
                    <div className="progress-fill fill-green" style={{width: `${result.scoring.category_scores.renewable_resource_score}%`}}></div>
                  </div>
                  <strong>{result.scoring.category_scores.renewable_resource_score}/100</strong>
                </li>
                <li>
                  <span>Terrain Suitability</span>
                  <div className="progress-bar-container">
                    <div className="progress-fill fill-blue" style={{width: `${result.scoring.category_scores.terrain_score}%`}}></div>
                  </div>
                  <strong>{result.scoring.category_scores.terrain_score}/100</strong>
                </li>
                <li>
                  <span>Infrastructure Proximity</span>
                  <div className="progress-bar-container">
                    <div className="progress-fill fill-purple" style={{width: `${result.scoring.category_scores.infrastructure_score}%`}}></div>
                  </div>
                  <strong>{result.scoring.category_scores.infrastructure_score}/100</strong>
                </li>
              </ul>
            </article>

            {/* Financial Card */}
            <article className="card financials-card">
              <h4>Economic Feasibility (Projected)</h4>
              <div className="metrics-box">
                <div className="metric-item">
                  <span className="label">Project Cost</span>
                  <strong className="value">₹{(result.financials.estimated_project_cost_inr / 10000000.0).toFixed(2)} Cr</strong>
                </div>
                <div className="metric-item">
                  <span className="label">Annual Revenue</span>
                  <strong className="value">₹{(result.financials.annual_revenue_inr / 100000).toFixed(2)} Lakhs</strong>
                </div>
                <div className="metric-item">
                  <span className="label">Payback Period</span>
                  <strong className="value">{result.financials.payback_period_years} Years</strong>
                </div>
                <div className="metric-item">
                  <span className="label">ROI</span>
                  <strong className="value">{result.financials.roi_percentage.toFixed(1)}%</strong>
                </div>
              </div>
            </article>

            {/* Energy Capacity */}
            <article className="card energy-card">
              <h4>Technical Output Specs</h4>
              <div className="metrics-box">
                <div className="metric-item">
                  <span className="label">Recommended Capacity</span>
                  <strong className="value">{result.technical_assessment.recommended_capacity_mw} MW</strong>
                </div>
                <div className="metric-item">
                  <span className="label">Annual Energy Yield</span>
                  <strong className="value">{result.energy.annual_energy_yield_kwh.toLocaleString()} kWh</strong>
                </div>
                <div className="metric-item">
                  <span className="label">Expansion Feasibility</span>
                  <strong className="value">{result.technical_assessment.expansion_status}</strong>
                </div>
              </div>
            </article>

            {/* ML Explainability */}
            <article className="card explainability-card full-width">
              <h4>ML Model Explanation (Solar GHI Predictor Importance)</h4>
              <p className="subtitle">Random Forest Regressor predicted GHI: <strong>{result.ml_predictions.predicted_ghi_kwh_m2_day} kWh/m²/day</strong></p>
              <div className="importance-grid">
                {result.ml_predictions.feature_importance.map((item) => (
                  <div key={item.feature} className="importance-bar">
                    <span className="feat-name">{item.feature}</span>
                    <div className="bar-track">
                      <div className="bar-fill" style={{width: `${item.importance * 100}%`}}></div>
                    </div>
                    <span className="feat-val">{(item.importance * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </article>
          </div>
        </section>
      )}
    </div>
  );
}

export default App;
