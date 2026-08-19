"use client";

import { useEffect, useState } from "react";
import "leaflet/dist/leaflet.css";

export interface SiteMarker {
  id: number;
  name: string;
  lat: number;
  lon: number;
  category: string;
  address?: string;
  land_area?: number | null;
  elevation?: number | null;
}

export default function SiteMap({ sites }: { sites: SiteMarker[] }) {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) {
    return (
      <div
        style={{
          height: "400px",
          background: "#f0f0f0",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          borderRadius: "8px",
          border: "1px solid #CBD5E0",
          fontFamily: "sans-serif",
          color: "#4A5568"
        }}
      >
        Loading Map...
      </div>
    );
  }

  const { MapContainer, TileLayer, Marker, Popup } = require("react-leaflet");
  const L = require("leaflet");

  delete L.Icon.Default.prototype._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/images/marker-icon-2x.png",
    iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/images/marker-icon.png",
    shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/images/marker-shadow.png",
  });

  const getMarkerIcon = (category: string) => {
    let color = "#718096";
    if (category === "Excellent")              color = "#6B46C1";
    else if (category === "Highly Suitable")   color = "#38A169";
    else if (category === "Moderately Suitable") color = "#3182CE";
    else if (category === "Low Suitability")   color = "#DD6B20";
    else if (category === "Unsuitable")        color = "#E53E3E";

    return new L.DivIcon({
      html: `<span style="background-color:${color};width:14px;height:14px;display:block;border-radius:50%;border:2px solid white;box-shadow:0 0 4px rgba(0,0,0,0.4)"></span>`,
      className: "custom-leaflet-icon",
      iconSize: [14, 14],
      iconAnchor: [7, 7],
    });
  };

  // Auto-centre on the mean of all site coordinates
  const center: [number, number] =
    sites.length > 0
      ? [
          sites.reduce((sum, s) => sum + s.lat, 0) / sites.length,
          sites.reduce((sum, s) => sum + s.lon, 0) / sites.length,
        ]
      : [20.0, 0.0];

  const zoom = sites.length > 0 ? 6 : 2;

  return (
    <div
      id="gis-leaflet-map"
      style={{
        height: "450px",
        width: "100%",
        borderRadius: "8px",
        overflow: "hidden",
        border: "1px solid #CBD5E0",
      }}
    >
      <MapContainer center={center} zoom={zoom} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {sites.map((site) => (
          <Marker
            key={site.id}
            position={[site.lat, site.lon]}
            icon={getMarkerIcon(site.category)}
          >
            <Popup>
              <div style={{ fontFamily: "sans-serif", fontSize: "12px", color: "#2D3748", minWidth: "160px" }}>
                <strong style={{ fontSize: "13px", display: "block", marginBottom: "4px" }}>
                  {site.name}
                </strong>

                {/* Site ID */}
                <div style={{ color: "#718096", marginBottom: "2px" }}>
                  ID: <strong>#{site.id}</strong>
                </div>

                {/* Suitability category */}
                <div style={{ marginBottom: "2px" }}>
                  Category:{" "}
                  <strong style={{ color: "#2B6CB0" }}>
                    {site.category !== "N/A" ? site.category : "Not scored yet"}
                  </strong>
                </div>

                {/* Coordinates */}
                <div style={{ marginBottom: "2px", color: "#4A5568" }}>
                  Lat: {site.lat.toFixed(5)}, Lon: {site.lon.toFixed(5)}
                </div>

                {/* Address if available */}
                {site.address && (
                  <div style={{ marginBottom: "2px", color: "#4A5568" }}>
                    📍 {site.address}
                  </div>
                )}

                {/* Land area */}
                {site.land_area != null && (
                  <div style={{ marginBottom: "2px", color: "#4A5568" }}>
                    Area: {site.land_area} acres
                  </div>
                )}

                {/* Elevation */}
                {site.elevation != null && (
                  <div style={{ marginBottom: "6px", color: "#4A5568" }}>
                    Elevation: {site.elevation} m
                  </div>
                )}

                <a
                  href={`/sites/${site.id}`}
                  style={{ color: "#3182CE", textDecoration: "none", fontWeight: "bold" }}
                >
                  View Full Details →
                </a>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
