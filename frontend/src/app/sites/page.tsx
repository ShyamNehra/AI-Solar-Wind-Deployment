"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import api from "../../services/api";

function SitesContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = searchParams ? searchParams.get("projectId") : null;

  const [sites, setSites] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [siteName, setSiteName] = useState("");
  const [lat, setLat] = useState("");
  const [lon, setLon] = useState("");
  const [area, setArea] = useState("");
  const [elevation, setElevation] = useState("");
  const [infra, setInfra] = useState("");
  const [ownership, setOwnership] = useState("");

  useEffect(() => {
    if (!projectId) return;
    async function loadSites() {
      try {
        const res = await api.get(`/projects/${projectId}/sites`);
        setSites(res.data);
      } catch (err) {
        alert("Failed to load sites.");
      } finally {
        setLoading(false);
      }
    }
    loadSites();
  }, [projectId]);

  const handleCreateSite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!siteName || !lat || !lon) return;
    try {
      const res = await api.post(`/projects/${projectId}/sites`, {
        name: siteName,
        latitude: parseFloat(lat),
        longitude: parseFloat(lon),
        land_area: area ? parseFloat(area) : null,
        elevation: elevation ? parseFloat(elevation) : null,
        existing_infrastructure: infra || null,
        land_ownership: ownership || null,
      });
      setSites([...sites, res.data]);
      setSiteName("");
      setLat("");
      setLon("");
      setArea("");
      setElevation("");
      setInfra("");
      setOwnership("");
    } catch (err) {
      alert("Failed to create site.");
    }
  };

  if (!projectId) return <p>No project ID specified.</p>;
  if (loading) return <p>Loading sites...</p>;

  return (
    <div style={{ padding: "2rem" }}>
      <button onClick={() => router.push("/dashboard")}>Back to Dashboard</button>
      <h1>Sites for Project {projectId}</h1>

      <h2>Add New Site</h2>
      <form onSubmit={handleCreateSite} style={{ marginBottom: "2rem" }}>
        <div style={{ marginBottom: "1rem" }}>
          <label>Site Name: </label>
          <input type="text" value={siteName} onChange={(e) => setSiteName(e.target.value)} required />
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label>Latitude: </label>
          <input type="number" step="any" value={lat} onChange={(e) => setLat(e.target.value)} required />
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label>Longitude: </label>
          <input type="number" step="any" value={lon} onChange={(e) => setLon(e.target.value)} required />
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label>Land Area (acres): </label>
          <input type="number" step="any" value={area} onChange={(e) => setArea(e.target.value)} />
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label>Elevation (m): </label>
          <input type="number" step="any" value={elevation} onChange={(e) => setElevation(e.target.value)} />
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label>Infrastructure: </label>
          <input type="text" value={infra} onChange={(e) => setInfra(e.target.value)} />
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label>Land Ownership: </label>
          <input type="text" value={ownership} onChange={(e) => setOwnership(e.target.value)} />
        </div>
        <button type="submit">Create Site</button>
      </form>

      <h2>Existing Sites</h2>
      {sites.length === 0 ? (
        <p>No sites found for this project.</p>
      ) : (
        <div>
          <ul style={{ listStyle: "none", padding: 0 }}>
            {sites.map((s) => (
              <li key={s.id} style={{
                marginBottom: "1rem",
                padding: "1rem",
                backgroundColor: "white",
                borderRadius: "8px",
                border: "1px solid #E2E8F0",
                boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center"
              }}>
                <div>
                  <strong style={{ fontSize: "1.1rem", color: "#2D3748" }}>{s.name}</strong>
                  <p style={{ margin: "4px 0 0 0", color: "#718096", fontSize: "0.9rem" }}>
                    Coordinates: ({s.latitude}, {s.longitude}) | Area: {s.land_area ?? 0} acres | Elevation: {s.elevation ?? 0}m
                  </p>
                </div>
                <div>
                  <button
                    onClick={() => router.push(`/sites/${s.id}`)}
                    style={{
                      padding: "0.5rem 1rem",
                      backgroundColor: "#3182CE",
                      color: "white",
                      border: "none",
                      borderRadius: "6px",
                      cursor: "pointer",
                      fontWeight: "bold",
                      fontSize: "0.85rem"
                    }}
                  >
                    View Details & Scores
                  </button>
                </div>
              </li>
            ))}
          </ul>
          {sites.length >= 2 && (
            <div style={{ marginTop: "1.5rem" }}>
              <button
                onClick={() => router.push(`/sites/compare?projectId=${projectId}&ids=${sites[0].id},${sites[1].id}`)}
                style={{
                  padding: "0.5rem 1rem",
                  backgroundColor: "#EDF2F7",
                  border: "1px solid #CBD5E0",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontWeight: "bold",
                  color: "#4A5568"
                }}
              >
                Compare First Two Sites
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function SitesPage() {
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <SitesContent />
    </Suspense>
  );
}
