import React from 'react';

export default function SiteCompare({ isOpen, onClose, sites = [], onRemove }) {
  // Sort sites in descending order of overall suitability score to prioritize investments (Module 7 specification)
  const prioritizedSites = [...sites].sort((a, b) => {
    const scoreA = parseFloat(a.site_suitability?.overall_score) || 0;
    const scoreB = parseFloat(b.site_suitability?.overall_score) || 0;
    return scoreB - scoreA;
  });

  return (
    <div className={`compare-drawer ${isOpen ? 'open' : ''}`}>
      <div className="compare-header">
        <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 800, color: '#0f172a' }}>
          Site Comparison Workspace
        </h2>
        <button 
          onClick={onClose}
          style={{
            background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: '#64748b'
          }}
        >
          &times;
        </button>
      </div>

      <p style={{ margin: '0 0 1.5rem 0', color: '#64748b', fontSize: '0.85rem' }}>
        Compare up to 4 registered deployment locations side-by-side.
      </p>

      {sites.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem 1rem', color: '#94a3b8' }}>
          <p style={{ margin: 0, fontSize: '0.9rem', fontWeight: 600 }}>No sites added to compare</p>
          <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.8rem' }}>Analyze sites and click "Add to Compare" to see them here.</p>
        </div>
      ) : (
        <div className="compare-list">
          {prioritizedSites.map((site, index) => {
            const isApproved = site.technical_feasibility?.final_status === 'APPROVED' || site.technical_feasibility?.is_technically_feasible;
            const statusColor = isApproved ? '#10b981' : '#ef4444';
            
            // Map back to correct parent index for deletion
            const originalIndex = sites.findIndex(s => 
              s.coordinates?.latitude === site.coordinates?.latitude && 
              s.coordinates?.longitude === site.coordinates?.longitude
            );

            return (
              <div key={index} className="compare-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                  <div>
                    <span style={{ fontSize: '0.7rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--accent-blue)' }}>
                      🏆 Priority Rank #{index + 1}
                    </span>
                    <h4 style={{ margin: '0.1rem 0 0 0', fontSize: '0.95rem', fontWeight: 800, color: '#0f172a' }}>
                      {site.site_id || `Site ${site.coordinates?.latitude}, ${site.coordinates?.longitude}`}
                    </h4>
                  </div>
                  <button 
                    onClick={() => onRemove(originalIndex)}
                    style={{
                      background: 'none', border: 'none', color: '#ef4444', fontSize: '0.8rem', cursor: 'pointer', fontWeight: 700
                    }}
                  >
                    Remove
                  </button>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.8rem' }}>
                  <div style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '0.4rem' }}>
                    <div style={{ color: '#64748b', fontSize: '0.7rem', fontWeight: 600 }}>PROJECT ID</div>
                    <strong>{site.project_id || 'N/A'}</strong>
                  </div>

                  <div style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '0.4rem' }}>
                    <div style={{ color: '#64748b', fontSize: '0.7rem', fontWeight: 600 }}>REGION</div>
                    <strong>{site.region || 'N/A'}</strong>
                  </div>

                  <div style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '0.4rem' }}>
                    <div style={{ color: '#64748b', fontSize: '0.7rem', fontWeight: 600 }}>ELEVATION</div>
                    <strong>{site.elevation ? (site.elevation.toString().toLowerCase().includes('m') ? site.elevation : `${site.elevation} m`) : 'N/A'}</strong>
                  </div>

                  <div style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '0.4rem', gridColumn: '1 / -1' }}>
                    <div style={{ color: '#64748b', fontSize: '0.7rem', fontWeight: 600 }}>EXISTING INFRASTRUCTURE</div>
                    <strong style={{ fontSize: '0.75rem' }}>{site.existing_infra || 'N/A'}</strong>
                  </div>

                  <div style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '0.4rem' }}>
                    <div style={{ color: '#64748b', fontSize: '0.7rem', fontWeight: 600 }}>STATUS</div>
                    <strong style={{ color: statusColor }}>
                      {site.technical_feasibility?.final_status || (isApproved ? 'APPROVED' : 'REJECTED')}
                    </strong>
                  </div>

                  <div style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '0.4rem' }}>
                    <div style={{ color: '#64748b', fontSize: '0.7rem', fontWeight: 600 }}>OVERALL SCORE</div>
                    <strong>{site.site_suitability?.overall_score || 'N/A'} / 100</strong>
                  </div>

                  <div style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '0.4rem' }}>
                    <div style={{ color: '#64748b', fontSize: '0.7rem', fontWeight: 600 }}>SOLAR IRR</div>
                    <strong>{site.site_suitability?.solar_irradiance_kwh_m2_day || 'N/A'} kWh</strong>
                  </div>

                  <div style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '0.4rem' }}>
                    <div style={{ color: '#64748b', fontSize: '0.7rem', fontWeight: 600 }}>WIND VELOCITY</div>
                    <strong>{site.site_suitability?.wind_speed_m_s || 'N/A'} m/s</strong>
                  </div>

                  <div style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '0.4rem' }}>
                    <div style={{ color: '#64748b', fontSize: '0.7rem', fontWeight: 600 }}>SLOPE</div>
                    <strong>{site.site_suitability?.terrain_slope_deg !== undefined ? `${site.site_suitability.terrain_slope_deg}°` : 'N/A'}</strong>
                  </div>

                  <div style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '0.4rem' }}>
                    <div style={{ color: '#64748b', fontSize: '0.7rem', fontWeight: 600 }}>ROI</div>
                    <strong>{site.financial_metrics?.roi_percentage !== undefined ? `${site.financial_metrics.roi_percentage}%` : 'N/A'}</strong>
                  </div>
                </div>

                {site.recommended_deployment && (
                  <div style={{ marginTop: '0.75rem', background: '#eff6ff', padding: '0.4rem 0.6rem', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 600, color: '#1e40af', textAlign: 'center' }}>
                    Tech Choice: {site.recommended_deployment.toUpperCase()}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
