import { useState } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMapEvents,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./index.css";

const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

const markerIcon = new L.Icon({
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

interface AnalysisResponse {
  location: {
    latitude: number;
    longitude: number;
  };

  location_validation?: {
    valid: boolean;
    location_type: string;
    reason: string;
    is_land: boolean;
  };

  environmental_data?: {
    solar_features?: any;
    wind_assessment?: any;
  };

  site_suitability?: {
    overall_score: number;
    recommendation: string;
  };

  recommended_deployment?: {
    technology: string;
    capacity_mw: number;
    expansion_status: string;
  };

  technical_feasibility?: {
    status: string;
    passed: boolean;
    failed_constraints: string[];
    soft_constraint_score: number;
  };

  energy_yield?: {
    annual_solar_energy_mwh: number;
    annual_wind_energy_mwh: number;
    total_annual_energy_mwh: number;
  };

  financial_metrics?: {
    electricity_tariff_rs_per_kwh: number;
    annual_revenue_rs: number;
    estimated_project_cost_rs: number;
    payback_period_years: number;
    roi_percent: number;
  };

  recommendation_reason?: string[];

  final_recommendation?: string;
}

interface MapClickProps {
  onSelect: (lat: number, lng: number) => void;
}

function MapClickHandler({ onSelect }: MapClickProps) {
  useMapEvents({
    click(event) {
      onSelect(event.latlng.lat, event.latlng.lng);
    },
  });

  return null;
}

function formatNumber(value: number | undefined, decimals = 0) {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return "0";
  }

  return value.toLocaleString("en-IN", {
    maximumFractionDigits: decimals,
    minimumFractionDigits: decimals,
  });
}

function formatMoney(value: number | undefined) {
  if (!value) return "₹0";

  if (value >= 1_000_000_000) {
    return `₹${(value / 1_000_000_000).toFixed(2)}B`;
  }

  if (value >= 1_000_000) {
    return `₹${(value / 1_000_000).toFixed(2)}M`;
  }

  return `₹${formatNumber(value)}`;
}

function App() {
  const [latitude, setLatitude] = useState(13.0827);
  const [longitude, setLongitude] = useState(80.2707);

  const [landArea, setLandArea] = useState(100);
  const [availableLand, setAvailableLand] = useState(70);
  const [installedCapacity, setInstalledCapacity] = useState(100);

  const [result, setResult] =
    useState<AnalysisResponse | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [activeTab, setActiveTab] = useState<
    "overview" | "resources" | "finance" | "technical"
  >("overview");

  const selectLocation = (lat: number, lng: number) => {
    setLatitude(Number(lat.toFixed(6)));
    setLongitude(Number(lng.toFixed(6)));

    setResult(null);
    setError("");
  };

  const analyzeSite = async () => {
    setLoading(true);
    setError("");

    try {
      const params = new URLSearchParams({
        latitude: String(latitude),
        longitude: String(longitude),
        land_area: String(landArea),
        available_land_percent: String(availableLand),
        installed_capacity: String(installedCapacity),
      });

      const response = await fetch(
        `${API_URL}/analysis?${params.toString()}`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail || "Analysis failed."
        );
      }

      setResult(data);
      setActiveTab("overview");
    } catch (err: any) {
      console.error(err);

      setError(
        err?.message ||
          "Unable to connect to the analysis backend."
      );
    } finally {
      setLoading(false);
    }
  };

  const validation = result?.location_validation;

  const isInvalidLocation =
    validation &&
    (!validation.valid || validation.is_land === false);

  const score =
    result?.site_suitability?.overall_score ?? 0;

  const technology =
    result?.recommended_deployment?.technology || "—";

  const totalEnergy =
    result?.energy_yield?.total_annual_energy_mwh ?? 0;

  const solarEnergy =
    result?.energy_yield?.annual_solar_energy_mwh ?? 0;

  const windEnergy =
    result?.energy_yield?.annual_wind_energy_mwh ?? 0;

  const solarContribution =
    totalEnergy > 0
      ? (solarEnergy / totalEnergy) * 100
      : 0;

  const windContribution =
    totalEnergy > 0
      ? (windEnergy / totalEnergy) * 100
      : 0;

  const recommendation =
    result?.final_recommendation ||
    result?.site_suitability?.recommendation ||
    "Awaiting Analysis";

  const recommendationLower =
    recommendation.toLowerCase();

  const isSuitable =
    recommendationLower.includes("suitable") &&
    !recommendationLower.includes("not suitable");

  const isConditional =
    recommendationLower.includes("conditional");

  const statusClass = isInvalidLocation
    ? "danger"
    : isConditional
    ? "warning"
    : isSuitable
    ? "success"
    : "neutral";

  return (
    <div className="app">
      {/* NAVBAR */}
      <header className="navbar">
        <div className="brand">
          <div className="brand-icon">⚡</div>

          <div>
            <h1>Renewable Intelligence</h1>
            <span>
              Solar & Wind Deployment Intelligence Platform
            </span>
          </div>
        </div>

        <div className="backend-status">
          <span className="status-dot" />
          Backend Connected
        </div>
      </header>

      {/* HERO */}
      <section className="hero">
        <div className="hero-content">
          <div className="eyebrow">
            AI-POWERED RENEWABLE ENERGY ANALYSIS
          </div>

          <h2>
            Discover the best
            <br />
            <span>renewable energy site.</span>
          </h2>

          <p>
            Analyse solar and wind potential, technical
            feasibility, energy yield and financial
            viability using the integrated analysis
            pipeline.
          </p>

          <div className="hero-tags">
            <span>☀ Solar Intelligence</span>
            <span>🌬 Wind Intelligence</span>
            <span>🤖 AI Decision Support</span>
          </div>
        </div>

        <div className="hero-badge">
          <div>♻</div>
          <strong>CLEAN</strong>
          <span>ENERGY</span>
        </div>
      </section>

      <main className="dashboard">
        {/* CONFIGURATION */}
        <section className="panel configuration">
          <div className="section-heading">
            <div>
              <span className="section-label">
                SITE ANALYSIS
              </span>
              <h3>Analyse a Site</h3>
              <p>
                Configure deployment parameters and select
                a location from the map.
              </p>
            </div>

            <div className="location-chip">
              📍 {latitude.toFixed(4)},{" "}
              {longitude.toFixed(4)}
            </div>
          </div>

          <div className="input-grid">
            <label>
              <span>Latitude</span>
              <input
                type="number"
                step="0.0001"
                value={latitude}
                onChange={(e) =>
                  setLatitude(Number(e.target.value))
                }
              />
            </label>

            <label>
              <span>Longitude</span>
              <input
                type="number"
                step="0.0001"
                value={longitude}
                onChange={(e) =>
                  setLongitude(Number(e.target.value))
                }
              />
            </label>

            <label>
              <span>Land Area</span>
              <div className="input-with-unit">
                <input
                  type="number"
                  min="1"
                  value={landArea}
                  onChange={(e) =>
                    setLandArea(Number(e.target.value))
                  }
                />
                <small>ha</small>
              </div>
            </label>

            <label>
              <span>Available Land</span>
              <div className="input-with-unit">
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={availableLand}
                  onChange={(e) =>
                    setAvailableLand(
                      Number(e.target.value)
                    )
                  }
                />
                <small>%</small>
              </div>
            </label>

            <label>
              <span>Installed Capacity</span>
              <div className="input-with-unit">
                <input
                  type="number"
                  min="1"
                  value={installedCapacity}
                  onChange={(e) =>
                    setInstalledCapacity(
                      Number(e.target.value)
                    )
                  }
                />
                <small>MW</small>
              </div>
            </label>
          </div>

          {/* MAP */}
          <div className="map-section">
            <div className="map-header">
              <div>
                <h4>Analysis Location</h4>
                <p>
                  Click anywhere on the map to select a
                  site.
                </p>
              </div>

              <div className="map-coordinates">
                {latitude.toFixed(4)} ,{" "}
                {longitude.toFixed(4)}
              </div>
            </div>

            <div className="map-wrapper">
              <MapContainer
                center={[latitude, longitude]}
                zoom={7}
                scrollWheelZoom={true}
                className="leaflet-map"
              >
                <TileLayer
                  attribution='&copy; OpenStreetMap contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                <MapClickHandler
                  onSelect={selectLocation}
                />

                <Marker
                  position={[latitude, longitude]}
                  icon={markerIcon}
                >
                  <Popup>
                    <strong>Selected Site</strong>
                    <br />
                    {latitude.toFixed(6)},{" "}
                    {longitude.toFixed(6)}
                  </Popup>
                </Marker>
              </MapContainer>

              <div className="map-overlay">
                <span>📍</span>
                Click the map to change location
              </div>
            </div>
          </div>

          {error && (
            <div className="error-box">
              <strong>Analysis Error</strong>
              <span>{error}</span>
            </div>
          )}

          <button
            className="analyze-button"
            onClick={analyzeSite}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner" />
                Analysing Site...
              </>
            ) : (
              <>
                ⚡ Analyse This Site
                <span>→</span>
              </>
            )}
          </button>
        </section>

        {/* RESULTS */}
        {result && (
          <section className="results">
            <div className="result-heading">
              <div>
                <span className="section-label">
                  ANALYSIS COMPLETE
                </span>

                <h3>Site Intelligence Report</h3>

                <p>
                  📍 {latitude.toFixed(4)} ,{" "}
                  {longitude.toFixed(4)}
                </p>
              </div>

              <div
                className={`recommendation-badge ${statusClass}`}
              >
                <span>
                  {isInvalidLocation
                    ? "🌊"
                    : isConditional
                    ? "⚠"
                    : isSuitable
                    ? "✓"
                    : "!"}
                </span>

                {isInvalidLocation
                  ? "Invalid Location"
                  : recommendation}
              </div>
            </div>

            {/* OCEAN / INVALID LOCATION */}
            {isInvalidLocation && (
              <div className="location-warning">
                <div className="warning-icon">🌊</div>

                <div>
                  <h3>
                    {validation?.location_type ||
                      "Invalid Location"}{" "}
                    detected
                  </h3>

                  <p>
                    {validation?.reason ||
                      "This location cannot be used for a land-based renewable energy deployment."}
                  </p>

                  <strong>
                    Please select a land-based location
                    from the map.
                  </strong>
                </div>
              </div>
            )}

            {/* TOP METRICS */}
            <div className="metric-grid">
              <div className="metric-card score-card">
                <div className="metric-title">
                  SITE SUITABILITY
                </div>

                <div className="score-layout">
                  <div
                    className="score-ring"
                    style={
                      {
                        "--score": `${score * 3.6}deg`,
                      } as React.CSSProperties
                    }
                  >
                    <div>
                      <strong>
                        {score.toFixed(2)}
                      </strong>
                      <span>/100</span>
                    </div>
                  </div>

                  <div>
                    <h4>
                      {result.site_suitability
                        ?.recommendation || "—"}
                    </h4>

                    <p>
                      AI-assisted suitability assessment
                      based on renewable resources, terrain
                      and deployment constraints.
                    </p>
                  </div>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-title">
                  RECOMMENDED DEPLOYMENT
                </div>

                <div className="big-value">
                  {technology}
                </div>

                <p>
                  {formatNumber(
                    result.recommended_deployment
                      ?.capacity_mw
                  )}{" "}
                  MW •{" "}
                  {
                    result.recommended_deployment
                      ?.expansion_status
                  }
                </p>

                <div className="technology-icon">
                  {technology === "Solar"
                    ? "☀"
                    : technology === "Wind"
                    ? "🌬"
                    : "☀ + 🌬"}
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-title">
                  ANNUAL ENERGY
                </div>

                <div className="big-value">
                  {formatNumber(totalEnergy)}
                </div>

                <p>MWh / year</p>

                <div className="mini-bar">
                  <span
                    style={{
                      width: `${solarContribution}%`,
                    }}
                  />
                  <span
                    style={{
                      width: `${windContribution}%`,
                    }}
                  />
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-title">
                  ANNUAL REVENUE
                </div>

                <div className="big-value">
                  {formatMoney(
                    result.financial_metrics
                      ?.annual_revenue_rs
                  )}
                </div>

                <p>projected yearly revenue</p>
              </div>

              <div className="metric-card">
                <div className="metric-title">
                  ROI
                </div>

                <div className="big-value">
                  {formatNumber(
                    result.financial_metrics?.roi_percent,
                    2
                  )}
                  %
                </div>

                <p>
                  Payback{" "}
                  {formatNumber(
                    result.financial_metrics
                      ?.payback_period_years,
                    2
                  )}{" "}
                  years
                </p>
              </div>
            </div>

            {/* TABS */}
            <div className="result-tabs">
              <button
                className={
                  activeTab === "overview"
                    ? "active"
                    : ""
                }
                onClick={() =>
                  setActiveTab("overview")
                }
              >
                Overview
              </button>

              <button
                className={
                  activeTab === "resources"
                    ? "active"
                    : ""
                }
                onClick={() =>
                  setActiveTab("resources")
                }
              >
                Resource Assessment
              </button>

              <button
                className={
                  activeTab === "finance"
                    ? "active"
                    : ""
                }
                onClick={() =>
                  setActiveTab("finance")
                }
              >
                Financial Analysis
              </button>

              <button
                className={
                  activeTab === "technical"
                    ? "active"
                    : ""
                }
                onClick={() =>
                  setActiveTab("technical")
                }
              >
                Technical Feasibility
              </button>
            </div>

            {/* OVERVIEW */}
            {activeTab === "overview" && (
              <div className="tab-content">
                <div className="content-grid">
                  <div className="content-card">
                    <div className="card-heading">
                      <span>⚡</span>
                      <div>
                        <h3>
                          Recommended Deployment
                        </h3>
                        <p>
                          Optimized technology based on
                          site resources.
                        </p>
                      </div>
                    </div>

                    <div className="deployment-display">
                      <div className="deployment-icon">
                        {technology === "Solar"
                          ? "☀"
                          : technology === "Wind"
                          ? "🌬"
                          : "☀🌬"}
                      </div>

                      <div>
                        <strong>
                          {technology}
                        </strong>

                        <span>
                          {
                            result
                              .recommended_deployment
                              ?.expansion_status
                          }
                        </span>
                      </div>

                      <div className="capacity">
                        <strong>
                          {formatNumber(
                            result
                              .recommended_deployment
                              ?.capacity_mw
                          )}
                        </strong>
                        <span>MW</span>
                      </div>
                    </div>
                  </div>

                  <div className="content-card">
                    <div className="card-heading">
                      <span>🤖</span>
                      <div>
                        <h3>
                          AI Recommendation Reasoning
                        </h3>
                        <p>
                          Factors generated by the
                          analysis pipeline.
                        </p>
                      </div>
                    </div>

                    <div className="reason-list">
                      {(
                        result.recommendation_reason ||
                        []
                      ).map((reason, index) => (
                        <div
                          className="reason-item"
                          key={index}
                        >
                          <span>✓</span>
                          {reason}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* RESOURCES */}
            {activeTab === "resources" && (
              <div className="tab-content">
                <div className="resource-grid">
                  <div className="resource-card solar">
                    <div className="resource-header">
                      <span>☀</span>
                      <div>
                        <h3>Solar Potential</h3>
                        <p>
                          Annual solar generation
                        </p>
                      </div>
                    </div>

                    <strong>
                      {formatNumber(solarEnergy)}
                    </strong>

                    <small>
                      MWh / year
                    </small>

                    <div className="contribution">
                      <div>
                        Contribution
                        <strong>
                          {solarContribution.toFixed(
                            1
                          )}
                          %
                        </strong>
                      </div>

                      <div className="progress">
                        <span
                          style={{
                            width: `${solarContribution}%`,
                          }}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="resource-card wind">
                    <div className="resource-header">
                      <span>🌬</span>
                      <div>
                        <h3>Wind Potential</h3>
                        <p>
                          Annual wind generation
                        </p>
                      </div>
                    </div>

                    <strong>
                      {formatNumber(windEnergy)}
                    </strong>

                    <small>
                      MWh / year
                    </small>

                    <div className="contribution">
                      <div>
                        Contribution
                        <strong>
                          {windContribution.toFixed(
                            1
                          )}
                          %
                        </strong>
                      </div>

                      <div className="progress">
                        <span
                          style={{
                            width: `${windContribution}%`,
                          }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="energy-total">
                  <span>⚡</span>
                  <div>
                    <small>
                      TOTAL ANNUAL ENERGY
                    </small>
                    <strong>
                      {formatNumber(totalEnergy)}{" "}
                      MWh
                    </strong>
                  </div>
                </div>
              </div>
            )}

            {/* FINANCE */}
            {activeTab === "finance" && (
              <div className="tab-content">
                <div className="finance-grid">
                  <div className="finance-card">
                    <span>Project Cost</span>
                    <strong>
                      {formatMoney(
                        result.financial_metrics
                          ?.estimated_project_cost_rs
                      )}
                    </strong>
                  </div>

                  <div className="finance-card">
                    <span>Annual Revenue</span>
                    <strong>
                      {formatMoney(
                        result.financial_metrics
                          ?.annual_revenue_rs
                      )}
                    </strong>
                  </div>

                  <div className="finance-card">
                    <span>Electricity Tariff</span>
                    <strong>
                      ₹
                      {formatNumber(
                        result.financial_metrics
                          ?.electricity_tariff_rs_per_kwh,
                        2
                      )}
                      /kWh
                    </strong>
                  </div>

                  <div className="finance-card">
                    <span>Payback Period</span>
                    <strong>
                      {formatNumber(
                        result.financial_metrics
                          ?.payback_period_years,
                        2
                      )}{" "}
                      years
                    </strong>
                  </div>

                  <div className="finance-card highlight">
                    <span>Return on Investment</span>
                    <strong>
                      {formatNumber(
                        result.financial_metrics
                          ?.roi_percent,
                        2
                      )}
                      %
                    </strong>
                  </div>
                </div>
              </div>
            )}

            {/* TECHNICAL */}
            {activeTab === "technical" && (
              <div className="tab-content">
                <div className="technical-card">
                  <div className="technical-status">
                    <div
                      className={
                        result.technical_feasibility
                          ?.passed
                          ? "status-circle success"
                          : "status-circle warning"
                      }
                    >
                      {result.technical_feasibility
                        ?.passed
                        ? "✓"
                        : "!"}
                    </div>

                    <div>
                      <span>
                        TECHNICAL STATUS
                      </span>

                      <h3>
                        {
                          result
                            .technical_feasibility
                            ?.status
                        }
                      </h3>
                    </div>
                  </div>

                  <div className="technical-stats">
                    <div>
                      <span>
                        Soft Constraint Score
                      </span>
                      <strong>
                        {formatNumber(
                          result
                            .technical_feasibility
                            ?.soft_constraint_score,
                          0
                        )}
                        /100
                      </strong>
                    </div>

                    <div>
                      <span>Expansion</span>
                      <strong>
                        {
                          result
                            .recommended_deployment
                            ?.expansion_status
                        }
                      </strong>
                    </div>
                  </div>

                  <div className="constraints">
                    <h4>
                      Constraints requiring attention
                    </h4>

                    {(
                      result.technical_feasibility
                        ?.failed_constraints || []
                    ).length === 0 ? (
                      <div className="no-constraints">
                        ✓ No failed hard constraints
                      </div>
                    ) : (
                      result.technical_feasibility?.failed_constraints.map(
                        (constraint, index) => (
                          <div
                            className="constraint-item"
                            key={index}
                          >
                            ⚠ {constraint}
                          </div>
                        )
                      )
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* FINAL RECOMMENDATION */}
            {!isInvalidLocation && (
              <div
                className={`final-recommendation ${statusClass}`}
              >
                <div className="final-icon">
                  {isConditional
                    ? "⚠"
                    : isSuitable
                    ? "✓"
                    : "!"}
                </div>

                <div>
                  <span>
                    FINAL RECOMMENDATION
                  </span>

                  <h2>{recommendation}</h2>

                  <p>
                    The recommendation combines resource
                    assessment, site suitability, technical
                    constraints, energy generation and
                    financial viability.
                  </p>
                </div>
              </div>
            )}
          </section>
        )}
      </main>

      <footer>
        <strong>
          Solar-Wind Deployment Intelligence Platform
        </strong>
        <span>
          • AI-assisted renewable energy planning
        </span>
      </footer>
    </div>
  );
}

export default App;