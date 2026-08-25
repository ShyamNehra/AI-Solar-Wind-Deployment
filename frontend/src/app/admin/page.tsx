"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  getAdminDataSources,
  getAdminUsers,
  getPlatformAnalytics
} from "../../services/dashboards";

export default function AdminPage() {
  const router = useRouter();
  const [dataSources, setDataSources] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadAdminData() {
      try {
        const sources = await getAdminDataSources();
        setDataSources(sources);
        
        const usersList = await getAdminUsers();
        setUsers(usersList);
        
        const stats = await getPlatformAnalytics();
        setAnalytics(stats);
      } catch (err: any) {
        setError("Unauthorized access. Admin privileges required.");
      } finally {
        setLoading(false);
      }
    }
    loadAdminData();
  }, []);

  if (loading) return <p style={{ padding: "2rem", fontFamily: "sans-serif" }}>Loading Admin Dashboard...</p>;
  if (error) return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <p style={{ color: "#E53E3E", fontWeight: "bold" }}>{error}</p>
      <button onClick={() => router.push("/dashboard")}>Back to Dashboard</button>
    </div>
  );

  return (
    <div style={{ fontFamily: "Segoe UI, sans-serif", backgroundColor: "#F7FAFC", minHeight: "100vh", padding: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <h1 style={{ margin: 0, color: "#1A365D" }}>Admin Console</h1>
        <button
          onClick={() => router.push("/dashboard")}
          style={{ padding: "0.5rem 1rem", backgroundColor: "#718096", color: "white", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: "bold" }}
        >
          Back to Dashboard
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem", marginBottom: "2rem" }}>
        
        {/* User Management Panel */}
        <section style={{ backgroundColor: "white", padding: "1.5rem", borderRadius: "12px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
          <h2 style={{ marginTop: 0, color: "#2B6CB0", fontSize: "1.2rem", borderBottom: "2px solid #E2E8F0", paddingBottom: "0.5rem" }}>
            User Role Management
          </h2>
          <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem" }}>
            <thead>
              <tr style={{ backgroundColor: "#F7FAFC", borderBottom: "2px solid #E2E8F0" }}>
                <th style={{ padding: "0.5rem", textAlign: "left" }}>ID</th>
                <th style={{ padding: "0.5rem", textAlign: "left" }}>Email</th>
                <th style={{ padding: "0.5rem", textAlign: "left" }}>Assigned Roles</th>
                <th style={{ padding: "0.5rem", textAlign: "center" }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} style={{ borderBottom: "1px solid #EDF2F7" }}>
                  <td style={{ padding: "0.5rem" }}>{u.id}</td>
                  <td style={{ padding: "0.5rem" }}>{u.email}</td>
                  <td style={{ padding: "0.5rem" }}>{u.roles.join(", ")}</td>
                  <td style={{ padding: "0.5rem", textAlign: "center" }}>
                    <span style={{ padding: "2px 6px", backgroundColor: u.is_active ? "#C6F6D5" : "#FED7D7", color: u.is_active ? "#22543D" : "#742A2A", borderRadius: "4px", fontSize: "0.8rem" }}>
                      {u.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        {/* Platform Analytics & Monitoring */}
        <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
          
          <section style={{ backgroundColor: "white", padding: "1.5rem", borderRadius: "12px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
            <h2 style={{ marginTop: 0, color: "#2B6CB0", fontSize: "1.2rem", borderBottom: "2px solid #E2E8F0", paddingBottom: "0.5rem" }}>
              Platform Analytics
            </h2>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginTop: "1rem" }}>
              <div style={{ padding: "1rem", backgroundColor: "#EDF2F7", borderRadius: "8px" }}>
                <span style={{ fontSize: "0.85rem", color: "#4A5568" }}>Total Projects</span>
                <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#2D3748" }}>{analytics?.total_projects}</div>
              </div>
              <div style={{ padding: "1rem", backgroundColor: "#EDF2F7", borderRadius: "8px" }}>
                <span style={{ fontSize: "0.85rem", color: "#4A5568" }}>Total Sites configured</span>
                <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#2D3748" }}>{analytics?.total_sites}</div>
              </div>
              <div style={{ padding: "1rem", backgroundColor: "#EDF2F7", borderRadius: "8px" }}>
                <span style={{ fontSize: "0.85rem", color: "#4A5568" }}>Cached MongoDB Payloads</span>
                <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#2D3748" }}>{analytics?.cached_environmental_payloads}</div>
              </div>
              <div style={{ padding: "1rem", backgroundColor: "#EDF2F7", borderRadius: "8px" }}>
                <span style={{ fontSize: "0.85rem", color: "#4A5568" }}>Total Energy Forecasts</span>
                <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#2D3748" }}>{analytics?.total_forecasts}</div>
              </div>
            </div>
          </section>

          <section style={{ backgroundColor: "white", padding: "1.5rem", borderRadius: "12px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
            <h2 style={{ marginTop: 0, color: "#2B6CB0", fontSize: "1.2rem", borderBottom: "2px solid #E2E8F0", paddingBottom: "0.5rem" }}>
              System Monitoring
            </h2>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "1rem", fontSize: "0.9rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "#718096" }}>Database engine:</span>
                <strong>PostgreSQL 16 + PostGIS</strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "#718096" }}>Secondary Cache:</span>
                <strong>MongoDB 7 (raw_environmental_cache)</strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "#718096" }}>System health status:</span>
                <span style={{ color: "#48BB78", fontWeight: "bold" }}>HEALTHY (running)</span>
              </div>
            </div>
          </section>

        </div>
      </div>

      {/* Data Sources & Assumptions Panel (Section 0) */}
      <section style={{ backgroundColor: "white", padding: "2rem", borderRadius: "12px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
        <h2 style={{ marginTop: 0, color: "#2B6CB0", fontSize: "1.3rem", borderBottom: "2px solid #E2E8F0", paddingBottom: "0.5rem", marginBottom: "1rem" }}>
          Data Sources & Platform Assumptions Audit
        </h2>
        <p style={{ color: "#718096", fontSize: "0.9rem", marginBottom: "1.5rem" }}>
          A canonical list of all non-real-data assumptions, physics proxies, and constants feeding the Solar & Wind intelligence engine:
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          {dataSources.map((source, index) => (
            <div
              key={source.key}
              style={{
                padding: "1rem 1.25rem",
                backgroundColor: "#F7FAFC",
                borderRadius: "8px",
                borderLeft: "4px solid #4299E1"
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                <strong style={{ color: "#2D3748", fontSize: "0.95rem" }}>
                  {index + 1}. {source.label}
                </strong>
                <span style={{ fontSize: "0.75rem", padding: "3px 8px", backgroundColor: "#EDF2F7", color: "#4A5568", borderRadius: "12px", fontWeight: "bold", textTransform: "uppercase" }}>
                  {source.status}
                </span>
              </div>
              <p style={{ margin: 0, fontSize: "0.85rem", color: "#4A5568", fontStyle: "italic", lineHeight: "1.4" }}>
                &ldquo;{source.disclosure}&rdquo;
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
