"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "../../services/api";
import { getMe, logout } from "../../services/auth";
import {
  getPlannerDashboard,
  getGisAnalystDashboard,
  getProjectManagerDashboard
} from "../../services/dashboards";
import {
  getNotifications,
  markNotificationAsRead
} from "../../services/notifications";
import SiteMap, { SiteMarker } from "../../components/SiteMap";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [projects, setProjects] = useState<any[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<string>("overview"); // overview, planner, gis, pm, optimize

  // Dashboard role-specific states
  const [plannerData, setPlannerData] = useState<any>(null);
  const [gisData, setGisData] = useState<any>(null);
  const [pmData, setPmData] = useState<any>(null);
  const [optData, setOptData] = useState<any>(null);

  // Live sites fetched directly from the DB for the map
  const [liveSites, setLiveSites] = useState<SiteMarker[]>([]);
  const [sitesLoading, setSitesLoading] = useState(false);

  // General states
  const [projectName, setProjectName] = useState("");
  const [projectDesc, setProjectDesc] = useState("");
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [dashLoading, setDashLoading] = useState(false);
  const [error, setError] = useState("");

  const isAdmin = user?.roles?.includes("Administrator");

  // Load user profile, projects, and notifications
  useEffect(() => {
    async function loadInitialData() {
      try {
        const u = await getMe();
        setUser(u);
        const projRes = await api.get("/projects");
        setProjects(projRes.data);
        
        // Load notifications
        const notifRes = await getNotifications();
        setNotifications(notifRes);
        
        if (projRes.data.length > 0) {
          setSelectedProjectId(projRes.data[0].id);
        }
      } catch (err: any) {
        setError("Failed to load dashboard. Redirecting to login...");
        setTimeout(() => {
          router.push("/login");
        }, 2000);
      } finally {
        setLoading(false);
      }
    }
    loadInitialData();
  }, [router]);

  // Load role-specific dashboard data when project or active tab changes
  useEffect(() => {
    if (selectedProjectId === null) return;
    const projId = selectedProjectId;

    async function loadDashboardData() {
      setDashLoading(true);
      try {
        if (activeTab === "planner") {
          const data = await getPlannerDashboard(projId);
          setPlannerData(data);
        } else if (activeTab === "gis") {
          const data = await getGisAnalystDashboard(projId);
          setGisData(data);
        } else if (activeTab === "pm") {
          const data = await getProjectManagerDashboard(projId);
          setPmData(data);
        } else if (activeTab === "optimize") {
          const optRes = await api.post(`/projects/${projId}/optimize`);
          setOptData(optRes.data);
        }
      } catch (err) {
        console.error("Failed to load dashboard tab data", err);
      } finally {
        setDashLoading(false);
      }
    }
    loadDashboardData();
  }, [selectedProjectId, activeTab]);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectName) return;
    try {
      const res = await api.post("/projects", {
        name: projectName,
        description: projectDesc,
      });
      setProjects([...projects, res.data]);
      setSelectedProjectId(res.data.id);
      setProjectName("");
      setProjectDesc("");
    } catch (err) {
      alert("Failed to create project.");
    }
  };

  const handleMarkAsRead = async (id: number) => {
    try {
      await markNotificationAsRead(id);
      setNotifications(notifications.map(n => n.id === id ? { ...n, is_read: true } : n));
    } catch (err) {
      alert("Failed to mark notification as read.");
    }
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (loading) return <p style={{ padding: "2rem", fontFamily: "sans-serif" }}>Loading dashboard...</p>;
  if (error) return <p style={{ padding: "2rem", fontFamily: "sans-serif" }}>{error}</p>;

  // Get current project
  const currentProject = projects.find(p => p.id === selectedProjectId);

  // Convert GIS Analyst data to markers
  const mapMarkers = (gisData?.gis_analyst_data || []).map((site: any) => ({
    id: site.site_id,
    name: site.site_name,
    lat: site.spatial_distribution.latitude,
    lon: site.spatial_distribution.longitude,
    category: plannerData?.recommended_sites?.find((s: any) => s.site_id === site.site_id)?.suitability_scores.category || "N/A"
  }));

  return (
    <div style={{ fontFamily: "Segoe UI, sans-serif", backgroundColor: "#F7FAFC", minHeight: "100vh", padding: "1.5rem" }}>
      {/* Top Navigation */}
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", backgroundColor: "white", padding: "1rem 1.5rem", borderRadius: "12px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ margin: 0, color: "#1A365D", fontSize: "1.5rem", fontWeight: "bold" }}>Solar & Wind platform</h1>
          <p style={{ margin: "4px 0 0 0", color: "#718096", fontSize: "0.85rem" }}>
            Logged in as: <strong>{user?.email}</strong> (Roles: {user?.roles?.join(", ")})
          </p>
        </div>
        <div style={{ display: "flex", gap: "10px" }}>
          {isAdmin && (
            <button
              onClick={() => router.push("/admin")}
              style={{ padding: "0.5rem 1rem", backgroundColor: "#2B6CB0", color: "white", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: "bold" }}
            >
              Admin Panel
            </button>
          )}
          <button
            onClick={handleLogout}
            style={{ padding: "0.5rem 1rem", backgroundColor: "#E53E3E", color: "white", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: "bold" }}
          >
            Logout
          </button>
        </div>
      </header>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 3fr", gap: "1.5rem" }}>
        
        {/* Left column: Projects and Notifications */}
        <aside style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          
          {/* Projects panel */}
          <div style={{ backgroundColor: "white", padding: "1.5rem", borderRadius: "12px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
            <h2 style={{ marginTop: 0, color: "#2D3748", fontSize: "1.2rem", borderBottom: "2px solid #E2E8F0", paddingBottom: "0.5rem" }}>Projects</h2>
            <ul style={{ listStyle: "none", padding: 0, margin: "1rem 0" }}>
              {projects.map((p) => (
                <li
                  key={p.id}
                  onClick={() => { setSelectedProjectId(p.id); setActiveTab("overview"); }}
                  style={{
                    padding: "0.75rem",
                    borderRadius: "8px",
                    cursor: "pointer",
                    backgroundColor: selectedProjectId === p.id ? "#EBF8FF" : "transparent",
                    color: selectedProjectId === p.id ? "#2B6CB0" : "#4A5568",
                    fontWeight: selectedProjectId === p.id ? "bold" : "normal",
                    marginBottom: "0.5rem",
                    transition: "all 0.2s"
                  }}
                >
                  {p.name}
                </li>
              ))}
            </ul>
            
            <h3 style={{ fontSize: "1rem", color: "#4A5568", marginTop: "1.5rem" }}>Create Project</h3>
            <form onSubmit={handleCreateProject}>
              <input
                type="text"
                placeholder="Project Name"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                required
                style={{ width: "100%", padding: "0.5rem", border: "1px solid #CBD5E0", borderRadius: "6px", marginBottom: "0.5rem", boxSizing: "border-box" }}
              />
              <input
                type="text"
                placeholder="Description"
                value={projectDesc}
                onChange={(e) => setProjectDesc(e.target.value)}
                style={{ width: "100%", padding: "0.5rem", border: "1px solid #CBD5E0", borderRadius: "6px", marginBottom: "0.75rem", boxSizing: "border-box" }}
              />
              <button type="submit" style={{ width: "100%", padding: "0.5rem", backgroundColor: "#48BB78", color: "white", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: "bold" }}>
                Add Project
              </button>
            </form>
          </div>

          {/* Notifications Panel */}
          <div style={{ backgroundColor: "white", padding: "1.5rem", borderRadius: "12px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
            <h2 style={{ marginTop: 0, color: "#2D3748", fontSize: "1.2rem", borderBottom: "2px solid #E2E8F0", paddingBottom: "0.5rem" }}>In-App Notifications</h2>
            {notifications.length === 0 ? (
              <p style={{ color: "#A0AEC0", fontSize: "0.85rem" }}>No notifications.</p>
            ) : (
              <div style={{ maxHeight: "300px", overflowY: "auto", marginTop: "1rem" }}>
                {notifications.map((n) => (
                  <div
                    key={n.id}
                    style={{
                      borderBottom: "1px solid #EDF2F7",
                      padding: "0.75rem 0",
                      opacity: n.is_read ? 0.6 : 1
                    }}
                  >
                    <strong style={{ fontSize: "0.9rem", color: "#2D3748" }}>{n.title}</strong>
                    <p style={{ margin: "4px 0", fontSize: "0.8rem", color: "#4A5568" }}>{n.message}</p>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "4px" }}>
                      <span style={{ fontSize: "0.7rem", color: "#A0AEC0" }}>
                        {new Date(n.created_at).toLocaleTimeString()}
                      </span>
                      {!n.is_read && (
                        <button
                          onClick={() => handleMarkAsRead(n.id)}
                          style={{ fontSize: "0.7rem", color: "#3182CE", background: "none", border: "none", cursor: "pointer", textDecoration: "underline" }}
                        >
                          Mark read
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
            <p style={{ margin: "10px 0 0 0", fontSize: "0.7rem", color: "#A0AEC0", fontStyle: "italic" }}>
              Delivery: in-app only, pending Module 12 email/push integration.
            </p>
          </div>
        </aside>

        {/* Right column: Main analytics content */}
        <main style={{ backgroundColor: "white", padding: "2rem", borderRadius: "12px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
          {currentProject ? (
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", borderBottom: "2px solid #E2E8F0", paddingBottom: "1rem", marginBottom: "1.5rem" }}>
                <div>
                  <h2 style={{ margin: 0, color: "#1A365D" }}>{currentProject.name}</h2>
                  <p style={{ margin: "4px 0 0 0", color: "#4A5568" }}>{currentProject.description}</p>
                </div>
                <button
                  onClick={() => router.push(`/sites?projectId=${currentProject.id}`)}
                  style={{ padding: "0.5rem 1rem", backgroundColor: "#EDF2F7", border: "1px solid #CBD5E0", borderRadius: "6px", cursor: "pointer", fontWeight: "bold", color: "#4A5568" }}
                >
                  Manage Sites list
                </button>
              </div>

              {/* Tabs list */}
              <div style={{ display: "flex", gap: "10px", marginBottom: "1.5rem", borderBottom: "1px solid #E2E8F0", paddingBottom: "0.5rem" }}>
                {[
                  { id: "overview", label: "Project Overview" },
                  { id: "planner", label: "Energy Planner" },
                  { id: "gis", label: "GIS Analyst" },
                  { id: "pm", label: "Project Manager" },
                  { id: "optimize", label: "Deployment Optimization" }
                ].map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    style={{
                      padding: "0.5rem 1rem",
                      border: "none",
                      background: activeTab === tab.id ? "#3182CE" : "none",
                      color: activeTab === tab.id ? "white" : "#4A5568",
                      borderRadius: "6px",
                      cursor: "pointer",
                      fontWeight: "bold",
                      transition: "all 0.2s"
                    }}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Tab views */}
              {dashLoading ? (
                <p>Loading tab metrics...</p>
              ) : (
                <div>
                  {activeTab === "overview" && (
                    <div>
                      <h3>Map Visualization</h3>
                      <p style={{ color: "#718096", fontSize: "0.85rem", marginBottom: "1rem" }}>
                        GIS map shows site locations color-coded by their suitability category. Click markers to view details.
                      </p>
                      {mapMarkers.length > 0 ? (
                        <SiteMap sites={mapMarkers} />
                      ) : (
                        <div style={{ padding: "2rem", backgroundColor: "#EDF2F7", borderRadius: "8px", textAlign: "center", color: "#718096" }}>
                          No geographic sites have been configured for this project yet. Use "Manage Sites list" to create sites.
                        </div>
                      )}
                    </div>
                  )}

                  {activeTab === "planner" && (
                    <div>
                      <h3>Energy Planner Dashboard</h3>
                      <p style={{ color: "#718096", fontSize: "0.85rem" }}>
                        Aggregates seasonal forecasts, suitability metrics, and capacity recommendations.
                      </p>
                      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem" }}>
                        <thead>
                          <tr style={{ backgroundColor: "#F7FAFC", borderBottom: "2px solid #E2E8F0" }}>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Site</th>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Suitability Score</th>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Solar Score</th>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Wind Score</th>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Tech Recommendation</th>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Capacity (kW)</th>
                            <th style={{ padding: "0.75rem", textAlign: "center" }}>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {(plannerData?.recommended_sites || []).map((site: any) => (
                            <tr key={site.site_id} style={{ borderBottom: "1px solid #EDF2F7" }}>
                              <td style={{ padding: "0.75rem" }}>
                                <strong>{site.site_name}</strong>
                              </td>
                              <td style={{ padding: "0.75rem" }}>
                                {site.suitability_scores.overall_score ?? "Unrated"} ({site.suitability_scores.category ?? "N/A"})
                              </td>
                              <td style={{ padding: "0.75rem" }}>{site.suitability_scores.solar_score ?? "N/A"}</td>
                              <td style={{ padding: "0.75rem" }}>{site.suitability_scores.wind_score ?? "N/A"}</td>
                              <td style={{ padding: "0.75rem" }}>
                                <span style={{ textTransform: "capitalize", padding: "3px 8px", backgroundColor: "#EBF8FF", borderRadius: "12px", fontSize: "0.8rem", color: "#2B6CB0", fontWeight: "bold" }}>
                                  {site.investment_recommendations.technology_recommendation ?? "N/A"}
                                </span>
                              </td>
                              <td style={{ padding: "0.75rem" }}>{site.investment_recommendations.recommended_capacity_kw ?? "N/A"}</td>
                              <td style={{ padding: "0.75rem", textAlign: "center" }}>
                                <button
                                  onClick={() => router.push(`/sites/${site.site_id}`)}
                                  style={{ padding: "3px 8px", backgroundColor: "#EDF2F7", border: "1px solid #CBD5E0", borderRadius: "4px", fontSize: "0.8rem", cursor: "pointer" }}
                                >
                                  Open details
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {plannerData?.data_note && (
                        <p style={{ marginTop: "1rem", fontSize: "0.75rem", color: "#A0AEC0", fontStyle: "italic" }}>
                          * Note: {plannerData.data_note}
                        </p>
                      )}
                    </div>
                  )}

                  {activeTab === "gis" && (
                    <div>
                      <h3>GIS Analyst Dashboard</h3>
                      <p style={{ color: "#718096", fontSize: "0.85rem" }}>
                        Verifies slope, elevation, spatial parameters, and infrastructure/setback proximity.
                      </p>
                      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem" }}>
                        <thead>
                          <tr style={{ backgroundColor: "#F7FAFC", borderBottom: "2px solid #E2E8F0" }}>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Site</th>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Elevation</th>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Slope</th>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Road Dist</th>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Substation Dist</th>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Water Dist</th>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Land Cover Type</th>
                          </tr>
                        </thead>
                        <tbody>
                          {(gisData?.gis_analyst_data || []).map((site: any) => (
                            <tr key={site.site_id} style={{ borderBottom: "1px solid #EDF2F7" }}>
                              <td style={{ padding: "0.75rem" }}><strong>{site.site_name}</strong></td>
                              <td style={{ padding: "0.75rem" }}>{site.spatial_distribution.elevation_m ? `${site.spatial_distribution.elevation_m}m` : "N/A"}</td>
                              <td style={{ padding: "0.75rem" }}>{site.spatial_distribution.slope_deg ? `${site.spatial_distribution.slope_deg}°` : "N/A"}</td>
                              <td style={{ padding: "0.75rem" }}>{site.proximity_analysis.nearest_road_km ? `${site.proximity_analysis.nearest_road_km.toFixed(2)} km` : "N/A"}</td>
                              <td style={{ padding: "0.75rem" }}>{site.proximity_analysis.nearest_substation_km ? `${site.proximity_analysis.nearest_substation_km.toFixed(2)} km` : "N/A"}</td>
                              <td style={{ padding: "0.75rem" }}>{site.proximity_analysis.nearest_water_body_km ? `${site.proximity_analysis.nearest_water_body_km.toFixed(2)} km` : "N/A"}</td>
                              <td style={{ padding: "0.75rem" }}>
                                {site.land_cover_suitability.land_cover_type}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                  {activeTab === "pm" && (
                    <div>
                      <h3>Project Manager Dashboard</h3>
                      <div style={{ padding: "1.25rem", backgroundColor: "#EDF2F7", borderRadius: "8px", marginBottom: "1.5rem", display: "inline-block" }}>
                        <span style={{ fontSize: "0.9rem", color: "#4A5568" }}>Overall Project Readiness Index: </span>
                        <strong style={{ fontSize: "1.5rem", color: "#2B6CB0", marginLeft: "10px" }}>
                          {pmData?.overall_project_readiness}%
                        </strong>
                      </div>

                      <h4>Cost-Benefit Analysis & Grid Distance Proximity</h4>
                      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "0.5rem" }}>
                        <thead>
                          <tr style={{ backgroundColor: "#F7FAFC", borderBottom: "2px solid #E2E8F0" }}>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Site</th>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Projected Year-1 Revenue</th>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Grid Distance</th>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Interconnection Score</th>
                          </tr>
                        </thead>
                        <tbody>
                          {(pmData?.cost_benefit_analysis || []).map((site: any) => (
                            <tr key={site.site_id} style={{ borderBottom: "1px solid #EDF2F7" }}>
                              <td style={{ padding: "0.75rem" }}><strong>{site.site_name}</strong></td>
                              <td style={{ padding: "0.75rem" }}>{site.cost_benefit_analysis.projected_annual_revenue_usd ? `$${site.cost_benefit_analysis.projected_annual_revenue_usd.toLocaleString()}` : "N/A"}</td>
                              <td style={{ padding: "0.75rem" }}>{site.cost_benefit_analysis.grid_interconnection_distance_km ? `${site.cost_benefit_analysis.grid_interconnection_distance_km.toFixed(2)} km` : "N/A"}</td>
                              <td style={{ padding: "0.75rem" }}>{site.cost_benefit_analysis.interconnection_cost_proxy_score ?? "N/A"}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>

                      <h4 style={{ marginTop: "1.5rem", color: "#E53E3E" }}>Risk & Expansion Flags</h4>
                      {(pmData?.expansion_risk_flags || []).length === 0 ? (
                        <p style={{ color: "#48BB78", fontWeight: "bold" }}>No risks flagged for this project.</p>
                      ) : (
                        <ul style={{ paddingLeft: "1.25rem", color: "#E53E3E" }}>
                          {(pmData.expansion_risk_flags).map((flag: any, idx: number) => (
                            <li key={idx} style={{ marginBottom: "0.5rem" }}>
                              <strong>{flag.site_name}</strong>: {flag.risk}
                            </li>
                          ))}
                        </ul>
                      )}
                      {pmData?.data_note && (
                        <p style={{ marginTop: "1rem", fontSize: "0.75rem", color: "#A0AEC0", fontStyle: "italic" }}>
                          * Note: {pmData.data_note}
                        </p>
                      )}
                    </div>
                  )}

                  {activeTab === "optimize" && (
                    <div>
                      <h3>Deployment Optimization Engine Results</h3>
                      <p style={{ color: "#718096", fontSize: "0.85rem" }}>
                        Runs the technology selection rules and calculates NREL density capacities based on site acreage.
                      </p>
                      <button
                        onClick={async () => {
                          setDashLoading(true);
                          try {
                            const optRes = await api.post(`/projects/${selectedProjectId}/optimize`);
                            setOptData(optRes.data);
                          } catch (e) {
                            alert("Optimization failed.");
                          } finally {
                            setDashLoading(false);
                          }
                        }}
                        style={{ padding: "0.5rem 1rem", backgroundColor: "#3182CE", color: "white", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: "bold", margin: "1rem 0" }}
                      >
                        Re-run Optimization Engine
                      </button>

                      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem" }}>
                        <thead>
                          <tr style={{ backgroundColor: "#F7FAFC", borderBottom: "2px solid #E2E8F0" }}>
                            <th style={{ padding: "0.75rem", textAlign: "center" }}>Rank</th>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Site</th>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Overall Score</th>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Solar / Wind</th>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Tech Rec</th>
                            <th style={{ padding: "0.75rem", textAlign: "left" }}>Recommended Capacity</th>
                            <th style={{ padding: "0.75rem", textAlign: "center" }}>Co-location Viable</th>
                          </tr>
                        </thead>
                        <tbody>
                          {(optData?.recommendations || []).map((rec: any) => (
                            <tr key={rec.site_id} style={{ borderBottom: "1px solid #EDF2F7" }}>
                              <td style={{ padding: "0.75rem", textAlign: "center" }}><strong>{rec.expansion_priority}</strong></td>
                              <td style={{ padding: "0.75rem" }}><strong>{rec.site_name}</strong></td>
                              <td style={{ padding: "0.75rem" }}>{rec.overall_deployment_score}</td>
                              <td style={{ padding: "0.75rem" }}>{rec.solar_score} / {rec.wind_score}</td>
                              <td style={{ padding: "0.75rem" }}>
                                <span style={{ textTransform: "capitalize", padding: "3px 8px", backgroundColor: "#EBF8FF", borderRadius: "12px", fontSize: "0.8rem", color: "#2B6CB0", fontWeight: "bold" }}>
                                  {rec.technology_recommendation}
                                </span>
                              </td>
                              <td style={{ padding: "0.75rem" }}><strong>{rec.recommended_capacity_kw} kW</strong></td>
                              <td style={{ padding: "0.75rem", textAlign: "center" }}>{rec.co_location_viability ? "Yes" : "No"}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <p>Please select a project to get started, or create one in the sidebar.</p>
          )}
        </main>
      </div>
    </div>
  );
}
