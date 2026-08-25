"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import api from "../../../services/api";
import { exportReport, triggerDownload } from "../../../services/reports";

export default function SiteDetailPage() {
  const params = useParams();
  const router = useRouter();
  const siteId = params ? params.id : null;

  const [site, setSite] = useState<any>(null);
  const [score, setScore] = useState<any>(null);
  const [solarPred, setSolarPred] = useState<any>(null);
  const [windPred, setWindPred] = useState<any>(null);
  const [forecast, setForecast] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [exportFormat, setExportFormat] = useState<"pdf" | "excel">("pdf");
  const [reportType, setReportType] = useState<"site_assessment" | "potential" | "feasibility">("site_assessment");
  const [exporting, setExporting] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    if (!siteId) return;

    async function loadSiteDetails() {
      try {
        // Fetch site basic info
        const siteRes = await api.get(`/sites/${siteId}`);
        setSite(siteRes.data);

        // Try getting scores
        try {
          const scoreRes = await api.post(`/sites/${siteId}/score`);
          setScore(scoreRes.data);
        } catch (e) {
          console.log("No score generated yet or scoring error");
          setScore(null);
        }

        // Try getting solar prediction
        try {
          const solarRes = await api.post(`/sites/${siteId}/predictions/solar`);
          setSolarPred(solarRes.data);
        } catch (e) {
          console.log("No solar prediction yet");
          setSolarPred(null);
        }

        // Try getting wind prediction
        try {
          const windRes = await api.post(`/sites/${siteId}/predictions/wind`);
          setWindPred(windRes.data);
        } catch (e) {
          console.log("No wind prediction yet");
          setWindPred(null);
        }

        // Try getting energy forecasts
        try {
          const seasonalRes = await api.post(`/sites/${siteId}/forecast/seasonal`);
          const longtermRes = await api.post(`/sites/${siteId}/forecast/longterm`);
          const revenueRes = await api.post(`/sites/${siteId}/forecast/revenue`);
          setForecast({
            seasonal: seasonalRes.data,
            longterm: longtermRes.data,
            revenue: revenueRes.data
          });
        } catch (e) {
          console.log("No energy forecast generated yet");
          setForecast(null);
        }

      } catch (err: any) {
        setError("Failed to load site details. Site might not exist or access is forbidden.");
      } finally {
        setLoading(false);
      }
    }
    loadSiteDetails();
  }, [siteId, refreshTrigger]);

  const handleRefreshEnvironmentalData = async () => {
    if (!siteId) return;
    setRefreshing(true);
    try {
      await api.post(`/sites/${siteId}/environmental/refresh`);
      setRefreshTrigger(prev => prev + 1);
      alert("Environmental data refreshed successfully!");
    } catch (e) {
      alert("Failed to refresh environmental data. Please verify your USGS and Copernicus credentials in the .env file.");
    } finally {
      setRefreshing(false);
    }
  };

  const handleExport = async () => {
    if (!siteId) return;
    setExporting(true);
    try {
      const blob = await exportReport(Number(siteId), exportFormat, reportType);
      const filename = `site_${siteId}_${reportType}_report.${exportFormat === 'pdf' ? 'pdf' : 'xlsx'}`;
      triggerDownload(blob, filename);
    } catch (e) {
      alert("Failed to export report.");
    } finally {
      setExporting(false);
    }
  };

  if (!siteId) return <p style={{ padding: "2rem", fontFamily: "sans-serif" }}>No site ID specified.</p>;
  if (loading) return <p style={{ padding: "2rem", fontFamily: "sans-serif" }}>Loading site metrics...</p>;
  if (error) return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <p style={{ color: "#E53E3E", fontWeight: "bold" }}>{error}</p>
      <button onClick={() => router.push("/dashboard")}>Back to Dashboard</button>
    </div>
  );

  return (
    <div style={{ fontFamily: "Segoe UI, sans-serif", backgroundColor: "#F7FAFC", minHeight: "100vh", padding: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <div>
          <button
            onClick={() => router.push("/dashboard")}
            style={{ border: "none", background: "none", color: "#3182CE", cursor: "pointer", fontWeight: "bold", padding: 0, marginBottom: "8px", display: "block" }}
          >
            &larr; Back to Dashboard
          </button>
          <h1 style={{ margin: 0, color: "#1A365D" }}>{site.name}</h1>
          <p style={{ margin: "4px 0 8px 0", color: "#718096" }}>
            Coordinates: ({site.latitude.toFixed(4)}, {site.longitude.toFixed(4)}) | Area: {site.land_area} acres
          </p>
          <button
            onClick={handleRefreshEnvironmentalData}
            disabled={refreshing}
            style={{
              padding: "0.5rem 1rem",
              backgroundColor: refreshing ? "#A0AEC0" : "#3182CE",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: refreshing ? "not-allowed" : "pointer",
              fontWeight: "bold",
              fontSize: "0.85rem",
              boxShadow: "0 1px 3px rgba(0,0,0,0.1)"
            }}
          >
            {refreshing ? "Refreshing Data..." : "Refresh Environmental Data"}
          </button>
        </div>
        
        {/* Report Export Box */}
        <div style={{ backgroundColor: "white", padding: "1rem", borderRadius: "8px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", display: "flex", gap: "10px", alignItems: "center" }}>
          <div>
            <label style={{ fontSize: "0.8rem", color: "#718096", display: "block", marginBottom: "3px" }}>Report Type</label>
            <select
              value={reportType}
              onChange={(e: any) => setReportType(e.target.value)}
              style={{ padding: "4px", borderRadius: "4px", border: "1px solid #CBD5E0" }}
            >
              <option value="site_assessment">Site Suitability</option>
              <option value="potential">Energy Potential</option>
              <option value="feasibility">Financial Feasibility</option>
            </select>
          </div>
          <div>
            <label style={{ fontSize: "0.8rem", color: "#718096", display: "block", marginBottom: "3px" }}>Format</label>
            <select
              value={exportFormat}
              onChange={(e: any) => setExportFormat(e.target.value)}
              style={{ padding: "4px", borderRadius: "4px", border: "1px solid #CBD5E0" }}
            >
              <option value="pdf">PDF File</option>
              <option value="excel">Excel Sheet</option>
            </select>
          </div>
          <button
            onClick={handleExport}
            disabled={exporting}
            style={{ padding: "0.5rem 1rem", backgroundColor: "#48BB78", color: "white", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: "bold", alignSelf: "flex-end" }}
          >
            {exporting ? "Downloading..." : "Download Report"}
          </button>
        </div>
      </div>

      {!score && (
        <div style={{
          backgroundColor: "#FFF5F5",
          border: "1px solid #FED7D7",
          color: "#C53030",
          padding: "1rem",
          borderRadius: "8px",
          marginBottom: "1.5rem"
        }}>
          <strong>No suitability scores available for this site yet.</strong> Please click the <strong>Refresh Environmental Data</strong> button above to query environmental, elevation, and terrain databases.
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>
        
        {/* Left Side: Predictions & Suitability scores */}
        <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
          
          {/* Suitability score card */}
          {score && (
            <section style={{ backgroundColor: "white", padding: "1.5rem", borderRadius: "12px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
              <h2 style={{ marginTop: 0, color: "#2B6CB0", fontSize: "1.2rem", borderBottom: "2px solid #E2E8F0", paddingBottom: "0.5rem" }}>
                Multi-Factor Suitability Scoring
              </h2>
              <div style={{ display: "flex", alignItems: "center", gap: "15px", marginTop: "1rem", marginBottom: "1.5rem" }}>
                <div style={{ padding: "1rem", backgroundColor: "#EBF8FF", borderRadius: "8px", textAlign: "center" }}>
                  <span style={{ fontSize: "0.85rem", color: "#2B6CB0" }}>Overall Suitability</span>
                  <div style={{ fontSize: "1.75rem", fontWeight: "bold", color: "#2B6CB0" }}>{score.overall_deployment_score}</div>
                </div>
                <div>
                  <strong style={{ fontSize: "1.1rem", color: "#2D3748" }}>{score.suitability_category}</strong>
                  <p style={{ margin: "4px 0 0 0", fontSize: "0.8rem", color: "#718096" }}>
                    Co-location hybrid potential calculated using a 50/50 mix of solar and wind overall scores.
                  </p>
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", fontSize: "0.9rem" }}>
                <div>Solar Sub-score: <strong>{score.solar_score}</strong></div>
                <div>Wind Sub-score: <strong>{score.wind_score}</strong></div>
                <div>Geographic Suitability: <strong>{score.geographic_score}</strong></div>
                <div>Infrastructure Proximity: <strong>{score.infrastructure_score}</strong></div>
                <div>Environmental Impact: <strong>{score.environmental_score}</strong></div>
                <div>Economic Feasibility: <strong>{score.economic_score}</strong></div>
              </div>
            </section>
          )}

          {/* Predictions card */}
          <section style={{ backgroundColor: "white", padding: "1.5rem", borderRadius: "12px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
            <h2 style={{ marginTop: 0, color: "#2B6CB0", fontSize: "1.2rem", borderBottom: "2px solid #E2E8F0", paddingBottom: "0.5rem" }}>
              Renewable Generation Predictions
            </h2>
            
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem", marginTop: "1rem" }}>
              {/* Solar Prediction */}
              {solarPred && (
                <div style={{ borderRight: "1px solid #E2E8F0", paddingRight: "1rem" }}>
                  <h3 style={{ margin: 0, color: "#D69E2E", fontSize: "1rem" }}>Solar resource</h3>
                  <div style={{ marginTop: "10px" }}>
                    <div style={{ fontSize: "0.85rem", color: "#718096" }}>Incident Irradiance</div>
                    <strong style={{ fontSize: "1.2rem" }}>{solarPred.annual_irradiance} kWh/m²/yr</strong>
                  </div>
                  <div style={{ marginTop: "10px" }}>
                    <div style={{ fontSize: "0.85rem", color: "#718096" }}>Expected Output (1kW)</div>
                    <strong style={{ fontSize: "1.2rem" }}>{solarPred.expected_energy_output} kWh/yr</strong>
                  </div>
                  <div style={{ marginTop: "10px" }}>
                    <div style={{ fontSize: "0.85rem", color: "#718096" }}>Capacity Factor</div>
                    <strong>{(solarPred.capacity_factor * 100).toFixed(2)}%</strong>
                  </div>
                </div>
              )}

              {/* Wind Prediction */}
              {windPred && (
                <div>
                  <h3 style={{ margin: 0, color: "#3182CE", fontSize: "1rem" }}>Wind resource</h3>
                  <div style={{ marginTop: "10px" }}>
                    <div style={{ fontSize: "0.85rem", color: "#718096" }}>Average Wind Speed</div>
                    <strong style={{ fontSize: "1.2rem" }}>{windPred.average_wind_speed} m/s</strong>
                  </div>
                  <div style={{ marginTop: "10px" }}>
                    <div style={{ fontSize: "0.85rem", color: "#718096" }}>Expected Output (2MW)</div>
                    <strong style={{ fontSize: "1.2rem" }}>{(windPred.expected_annual_energy_production / 1000).toFixed(1)} MWh/yr</strong>
                  </div>
                  <div style={{ marginTop: "10px" }}>
                    <div style={{ fontSize: "0.85rem", color: "#718096" }}>Capacity Factor</div>
                    <strong>{(windPred.capacity_factor * 100).toFixed(2)}%</strong>
                  </div>
                </div>
              )}
            </div>
          </section>

        </div>

        {/* Right Side: Generation & Revenue forecasts */}
        <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
          
          {/* Energy Forecasts card */}
          {forecast && (
            <section style={{ backgroundColor: "white", padding: "1.5rem", borderRadius: "12px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
              <h2 style={{ marginTop: 0, color: "#2B6CB0", fontSize: "1.2rem", borderBottom: "2px solid #E2E8F0", paddingBottom: "0.5rem" }}>
                Seasonal & Long-Term Generation Forecasts
              </h2>

              <h3 style={{ fontSize: "0.95rem", color: "#4A5568", marginTop: "1rem" }}>Year-1 Monthly Breakdown (kWh)</h3>
              <div style={{ maxHeight: "200px", overflowY: "auto", border: "1px solid #EDF2F7", borderRadius: "6px", marginTop: "0.5rem" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
                  <thead>
                    <tr style={{ backgroundColor: "#F7FAFC", borderBottom: "1px solid #E2E8F0" }}>
                      <th style={{ padding: "4px 8px", textAlign: "left" }}>Month</th>
                      <th style={{ padding: "4px 8px", textAlign: "right" }}>Solar kWh</th>
                      <th style={{ padding: "4px 8px", textAlign: "right" }}>Wind kWh</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.keys(forecast.seasonal.solar_seasonal_kwh).map(m => (
                      <tr key={m} style={{ borderBottom: "1px solid #EDF2F7" }}>
                        <td style={{ padding: "4px 8px" }}>{m}</td>
                        <td style={{ padding: "4px 8px", textAlign: "right" }}>{forecast.seasonal.solar_seasonal_kwh[m].toFixed(1)}</td>
                        <td style={{ padding: "4px 8px", textAlign: "right" }}>{forecast.seasonal.wind_seasonal_kwh[m].toFixed(1)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <h3 style={{ fontSize: "0.95rem", color: "#4A5568", marginTop: "1.5rem" }}>20-Year Production Projections (with degradation)</h3>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginTop: "0.5rem", fontSize: "0.85rem" }}>
                <div>
                  <strong>Solar Output</strong>
                  <div style={{ display: "flex", justifyContent: "space-between", marginTop: "5px" }}>
                    <span>Year 1:</span>
                    <strong>{forecast.longterm.solar_longterm_kwh[0]?.toFixed(1)} kWh</strong>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>Year 10:</span>
                    <strong>{forecast.longterm.solar_longterm_kwh[9]?.toFixed(1)} kWh</strong>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>Year 20:</span>
                    <strong>{forecast.longterm.solar_longterm_kwh[19]?.toFixed(1)} kWh</strong>
                  </div>
                </div>

                <div>
                  <strong>Wind Output</strong>
                  <div style={{ display: "flex", justifyContent: "space-between", marginTop: "5px" }}>
                    <span>Year 1:</span>
                    <strong>{(forecast.longterm.wind_longterm_kwh[0]/1000)?.toFixed(1)} MWh</strong>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>Year 10:</span>
                    <strong>{(forecast.longterm.wind_longterm_kwh[9]/1000)?.toFixed(1)} MWh</strong>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>Year 20:</span>
                    <strong>{(forecast.longterm.wind_longterm_kwh[19]/1000)?.toFixed(1)} MWh</strong>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Revenue Forecasts card */}
          {forecast && (
            <section style={{ backgroundColor: "white", padding: "1.5rem", borderRadius: "12px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
              <h2 style={{ marginTop: 0, color: "#2B6CB0", fontSize: "1.2rem", borderBottom: "2px solid #E2E8F0", paddingBottom: "0.5rem" }}>
                Financial Analysis & Grid Contribution
              </h2>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginTop: "1rem" }}>
                <div style={{ padding: "1rem", backgroundColor: "#EDF2F7", borderRadius: "8px" }}>
                  <span style={{ fontSize: "0.85rem", color: "#4A5568" }}>Combined Year-1 Revenue</span>
                  <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#2B6CB0" }}>
                    ${forecast.revenue.combined_annual_revenue.toLocaleString()}
                  </div>
                </div>
                <div style={{ padding: "1rem", backgroundColor: "#EDF2F7", borderRadius: "8px" }}>
                  <span style={{ fontSize: "0.85rem", color: "#4A5568" }}>Grid Contribution ratio</span>
                  <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#2D3748" }}>
                    {(forecast.revenue.grid_contribution_ratio * 100).toFixed(4)}%
                  </div>
                </div>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", marginTop: "1rem", fontSize: "0.85rem", color: "#718096" }}>
                <span>Electricity Price Baseline:</span>
                <strong>${forecast.revenue.electricity_rate_usd_kwh} / kWh</strong>
              </div>
            </section>
          )}

        </div>

      </div>
    </div>
  );
}
