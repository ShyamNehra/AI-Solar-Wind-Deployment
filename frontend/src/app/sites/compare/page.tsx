"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import api from "../../../services/api";

function CompareContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = searchParams ? searchParams.get("projectId") : null;
  const ids = searchParams ? searchParams.get("ids") : null;

  const [comparison, setComparison] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!projectId || !ids) return;
    async function loadComparison() {
      try {
        const res = await api.get(`/projects/${projectId}/sites/compare?ids=${ids}`);
        setComparison(res.data);
      } catch (err) {
        setError("Failed to load site comparison.");
      } finally {
        setLoading(false);
      }
    }
    loadComparison();
  }, [projectId, ids]);

  if (!projectId || !ids) return <p>Missing parameters for comparison.</p>;
  if (loading) return <p>Loading comparison...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div style={{ padding: "2rem" }}>
      <button onClick={() => router.push(`/sites?projectId=${projectId}`)}>
        Back to Sites
      </button>
      <h1>Site Comparison</h1>

      <div style={{ display: "flex", gap: "2rem", marginTop: "2rem" }}>
        <div style={{ border: "1px solid #ccc", padding: "1rem", flex: 1 }}>
          <h3>Site 1: {comparison.site1.name}</h3>
          <p>Latitude: {comparison.site1.latitude}</p>
          <p>Longitude: {comparison.site1.longitude}</p>
          <p>Elevation: {comparison.site1.elevation}m</p>
          <p>Area: {comparison.site1.land_area} acres</p>
          <p>Infrastructure: {comparison.site1.existing_infrastructure}</p>
          <p>Ownership: {comparison.site1.land_ownership}</p>
        </div>

        <div style={{ border: "1px solid #ccc", padding: "1rem", flex: 1 }}>
          <h3>Site 2: {comparison.site2.name}</h3>
          <p>Latitude: {comparison.site2.latitude}</p>
          <p>Longitude: {comparison.site2.longitude}</p>
          <p>Elevation: {comparison.site2.elevation}m</p>
          <p>Area: {comparison.site2.land_area} acres</p>
          <p>Infrastructure: {comparison.site2.existing_infrastructure}</p>
          <p>Ownership: {comparison.site2.land_ownership}</p>
        </div>
      </div>

      <div style={{ marginTop: "2rem", padding: "1rem", backgroundColor: "#f9f9f9" }}>
        <h3>Comparison Metrics</h3>
        <p><strong>Distance Between Sites:</strong> {comparison.distance_km.toFixed(2)} km</p>
        <p><strong>Elevation Difference:</strong> {comparison.elevation_difference.toFixed(2)} m</p>
      </div>
    </div>
  );
}

export default function ComparePage() {
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <CompareContent />
    </Suspense>
  );
}
