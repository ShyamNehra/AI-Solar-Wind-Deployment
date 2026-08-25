"use client";

import { useEffect, useState, Suspense } from "react";
import { useParams, useRouter } from "next/navigation";
import api from "../../../../services/api";

function OptimizeContent() {
  const params = useParams();
  const router = useRouter();
  const projectId = params ? params.id : null;

  const [optData, setOptData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!projectId) return;

    async function loadOptimization() {
      try {
        const res = await api.post(`/projects/${projectId}/optimize`);
        setOptData(res.data);
      } catch (err: any) {
        setError("Failed to run deployment optimization. Ensure sites have scores generated.");
      } finally {
        setLoading(false);
      }
    }
    loadOptimization();
  }, [projectId]);

  if (!projectId) return <p style={{ padding: "2rem", fontFamily: "sans-serif" }}>No project ID specified.</p>;
  if (loading) return <p style={{ padding: "2rem", fontFamily: "sans-serif" }}>Running deployment optimization engine...</p>;
  if (error) return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <p style={{ color: "#E53E3E", fontWeight: "bold" }}>{error}</p>
      <button onClick={() => router.push("/dashboard")} style={{ padding: "0.5rem 1rem", backgroundColor: "#3182CE", color: "white", border: "none", borderRadius: "6px", cursor: "pointer" }}>
        Back to Dashboard
      </button>
    </div>
  );

  return (
    <div style={{ fontFamily: "Segoe UI, sans-serif", backgroundColor: "#F7FAFC", minHeight: "100vh", padding: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem", borderBottom: "2px solid #E2E8F0", paddingBottom: "1rem" }}>
        <div>
          <button
            onClick={() => router.push("/dashboard")}
            style={{ border: "none", background: "none", color: "#3182CE", cursor: "pointer", fontWeight: "bold", padding: 0, marginBottom: "8px", display: "block" }}
          >
            &larr; Back to Dashboard
          </button>
          <h1 style={{ margin: 0, color: "#1A365D" }}>Deployment Optimization Rankings</h1>
          <p style={{ margin: "4px 0 0 0", color: "#718096" }}>
            Project ID: <strong>{projectId}</strong>
          </p>
        </div>
      </div>

      <div style={{ backgroundColor: "white", padding: "2rem", borderRadius: "12px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", marginBottom: "2rem" }}>
        <h2 style={{ marginTop: 0, color: "#2B6CB0", fontSize: "1.2rem", borderBottom: "1px solid #EDF2F7", paddingBottom: "0.5rem" }}>
          Optimized Technology Selection & Capacity Planning
        </h2>
        <p style={{ color: "#718096", fontSize: "0.9rem", marginBottom: "1.5rem" }}>
          Sites ranked descending by overall co-location suitability score. Capacity planning converts land area (acres) to square meters and applies NREL density guidelines.
        </p>

        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" }}>
          <thead>
            <tr style={{ backgroundColor: "#F7FAFC", borderBottom: "2px solid #E2E8F0" }}>
              <th style={{ padding: "0.75rem", textAlign: "center" }}>Rank (Priority)</th>
              <th style={{ padding: "0.75rem", textAlign: "left" }}>Site ID</th>
              <th style={{ padding: "0.75rem", textAlign: "left" }}>Name</th>
              <th style={{ padding: "0.75rem", textAlign: "left" }}>Overall Score</th>
              <th style={{ padding: "0.75rem", textAlign: "left" }}>Solar / Wind</th>
              <th style={{ padding: "0.75rem", textAlign: "left" }}>Tech Recommendation</th>
              <th style={{ padding: "0.75rem", textAlign: "left" }}>Recommended Capacity</th>
              <th style={{ padding: "0.75rem", textAlign: "center" }}>Co-location Viable</th>
            </tr>
          </thead>
          <tbody>
            {(optData?.recommendations || []).map((rec: any) => (
              <tr key={rec.site_id} style={{ borderBottom: "1px solid #EDF2F7" }}>
                <td style={{ padding: "0.75rem", textAlign: "center" }}>
                  <strong style={{ fontSize: "1.1rem", color: "#2D3748" }}>{rec.expansion_priority}</strong>
                </td>
                <td style={{ padding: "0.75rem" }}>{rec.site_id}</td>
                <td style={{ padding: "0.75rem" }}>
                  <strong>{rec.site_name}</strong>
                </td>
                <td style={{ padding: "0.75rem" }}>{rec.overall_deployment_score.toFixed(2)}</td>
                <td style={{ padding: "0.75rem" }}>{rec.solar_score.toFixed(2)} / {rec.wind_score.toFixed(2)}</td>
                <td style={{ padding: "0.75rem" }}>
                  <span
                    style={{
                      textTransform: "capitalize",
                      padding: "3px 8px",
                      backgroundColor: rec.technology_recommendation === "hybrid" ? "#EBF8FF" : rec.technology_recommendation === "solar" ? "#FEFCBF" : "#E6FFFA",
                      color: rec.technology_recommendation === "hybrid" ? "#2B6CB0" : rec.technology_recommendation === "solar" ? "#B7791F" : "#319795",
                      borderRadius: "12px",
                      fontSize: "0.8rem",
                      fontWeight: "bold"
                    }}
                  >
                    {rec.technology_recommendation}
                  </span>
                </td>
                <td style={{ padding: "0.75rem" }}>
                  <strong>{rec.recommended_capacity_kw.toFixed(2)} kW</strong>
                </td>
                <td style={{ padding: "0.75rem", textAlign: "center" }}>
                  {rec.co_location_viability ? (
                    <span style={{ color: "#48BB78", fontWeight: "bold" }}>Yes</span>
                  ) : (
                    <span style={{ color: "#E53E3E", fontWeight: "bold" }}>No</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Sources & Assumptions notes */}
      <div style={{ backgroundColor: "#EDF2F7", padding: "1.25rem", borderRadius: "8px", fontSize: "0.8rem", color: "#4A5568" }}>
        <h4 style={{ margin: "0 0 8px 0" }}>Capacity Density Sources:</h4>
        <ul style={{ margin: 0, paddingLeft: "1.25rem", lineHeight: "1.5" }}>
          <li>{optData?.capacity_density_solar_source}</li>
          <li>{optData?.capacity_density_wind_source}</li>
        </ul>
      </div>
    </div>
  );
}

export default function OptimizePage() {
  return (
    <Suspense fallback={<p style={{ padding: "2rem", fontFamily: "sans-serif" }}>Loading...</p>}>
      <OptimizeContent />
    </Suspense>
  );
}
