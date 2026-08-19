import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Standard Default Marker Icon
import defaultIconImg from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

// SVG Custom Markers for Feasibility Statuses
const createCustomIcon = (colorHex) => {
  const svgMarker = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 36" width="28" height="42">
      <path fill="${colorHex}" stroke="#ffffff" stroke-width="1.5" d="M12 0C5.37 0 0 5.37 0 12c0 9 12 24 12 24s12-15 12-24c0-6.63-5.37-12-12-12zm0 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/>
    </svg>`;
  return L.divIcon({
    className: 'custom-leaflet-marker',
    html: svgMarker,
    iconSize: [28, 42],
    iconAnchor: [14, 42],
    popupAnchor: [0, -38]
  });
};

const statusIcons = {
  approved: createCustomIcon('#10b981'),  // Emerald Green
  rejected: createCustomIcon('#ef4444'),  // Crimson Red
  warning: createCustomIcon('#f59e0b'),   // Amber Yellow
  default: L.icon({
    iconUrl: defaultIconImg,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34]
  })
};

// Helper component to smoothly center/fly map to updated coordinates & invalidate size on resize
function MapRecenter({ position }) {
  const map = useMap();
  useEffect(() => {
    try {
      map.invalidateSize();
    } catch (e) {
      // ignore
    }
    if (position && position[0] && position[1]) {
      map.flyTo(position, map.getZoom(), { animate: true });
    }
  }, [position, map]);
  return null;
}

// Child component handling map click events
function LocationMarker({ onMapClick, position, feasibilityResult }) {
  useMapEvents({
    click(e) {
      onMapClick(e.latlng.lat.toFixed(4), e.latlng.lng.toFixed(4));
    },
  });

  if (!position) return null;

  // Determine status color icon based on GIS feasibility response
  let markerIcon = statusIcons.default;
  let statusBadgeColor = '#64748b';
  let statusLabel = 'Selected Coordinates';

  if (feasibilityResult) {
    const { is_feasible, land_type, site_name } = feasibilityResult;

    if (land_type === 'gis_unverified_pass') {
      markerIcon = statusIcons.warning;
      statusBadgeColor = '#d97706';
      statusLabel = 'ℹ️ Local Geofence Verified';
    } else if (!is_feasible || land_type) {
      markerIcon = statusIcons.rejected;
      statusBadgeColor = '#dc2626';
      statusLabel = `🚫 REJECTED (${land_type?.replace('_', ' ').toUpperCase() || 'RESTRICTED'})`;
    } else {
      markerIcon = statusIcons.approved;
      statusBadgeColor = '#059669';
      statusLabel = '✅ APPROVED SITE';
    }
  }

  return (
    <Marker position={position} icon={markerIcon}>
      <Popup>
        <div style={{ fontFamily: 'sans-serif', padding: '2px 4px' }}>
          <span style={{
            display: 'inline-block',
            backgroundColor: statusBadgeColor,
            color: '#ffffff',
            padding: '3px 8px',
            borderRadius: '4px',
            fontSize: '11px',
            fontWeight: 'bold',
            marginBottom: '6px'
          }}>
            {statusLabel}
          </span>

          <div style={{ fontSize: '13px', color: '#1e293b', fontWeight: '600' }}>
            {feasibilityResult?.site_name || 'Selected Location'}
          </div>

          <div style={{ fontSize: '11px', color: '#64748b', marginTop: '4px' }}>
            Lat: {position[0]}, Lng: {position[1]}
          </div>

          {feasibilityResult?.reason && (
            <div style={{ fontSize: '11px', color: '#dc2626', marginTop: '6px', fontStyle: 'italic' }}>
              {feasibilityResult.reason}
            </div>
          )}
        </div>
      </Popup>
    </Marker>
  );
}

export default function SiteMap({ latitude, longitude, onLocationSelect, feasibilityResult }) {
  const position = [parseFloat(latitude) || 26.9124, parseFloat(longitude) || 75.7873];

  return (
    <div className="sitemap-container" style={{ height: '100%', minHeight: '260px', width: '100%', borderRadius: '8px', overflow: 'hidden', margin: 0 }}>
      <MapContainer center={position} zoom={8} style={{ height: '100%', width: '100%', minHeight: '260px' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapRecenter position={position} />
        <LocationMarker 
          onMapClick={onLocationSelect} 
          position={position} 
          feasibilityResult={feasibilityResult} 
        />
      </MapContainer>
    </div>
  );
}