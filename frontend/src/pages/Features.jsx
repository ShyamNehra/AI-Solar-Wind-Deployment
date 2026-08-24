import { useState, useEffect, useMemo } from 'react'
import { featuresAPI, sitesAPI, projectsAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import AlertMessage from '../components/AlertMessage'
import CircularProgress from '../components/CircularProgress'
import sortFeatureData from '../utils/sorting'
import * as XLSX from 'xlsx'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement,
  PointElement, LineElement, ArcElement, RadialLinearScale,
  Tooltip, Legend, Filler
} from 'chart.js'
import { Bar, Line, Doughnut, Radar } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale, LinearScale, BarElement,
  PointElement, LineElement, ArcElement, RadialLinearScale,
  Tooltip, Legend, Filler
)

const WIND_CLASSES    = ['All', 'Poor', 'Moderate', 'Good', 'Excellent']
const SORT_FIELDS     = [
  { label: 'ID',                 value: 'id' },
  { label: 'Latitude',           value: 'latitude' },
  { label: 'Longitude',          value: 'longitude' },
  { label: 'Solar Irradiance',   value: 'solar_irradiance' },
  { label: 'Wind Speed',         value: 'wind_speed' },
  { label: 'Temperature',        value: 'temperature' },
  { label: 'Humidity',           value: 'humidity' },
  { label: 'Elevation',          value: 'elevation' },
  { label: 'Slope',              value: 'slope' },
  { label: 'Road Distance',      value: 'road_distance' },
  { label: 'Substation Distance',value: 'substation_distance' },
  { label: 'Capacity Factor',    value: 'capacity_factor' },
  { label: 'Wind Class',         value: 'wind_class' },
  { label: 'Terrain Score',      value: 'terrain_score' },
  { label: 'Accessibility',      value: 'accessibility_score' },
  { label: 'Date',               value: 'created_at' },
]

// ── Engineered features ───────────────────────────────────────────────────────
function computeEngineered(f) {
  const solar = f.solar_irradiance || 0
  const wind  = f.wind_speed       || 0
  const elev  = f.elevation        || 0
  const slope = f.slope            || 0
  const road  = f.road_distance    || 0
  const sub   = f.substation_distance || 0
  const terr  = f.terrain_score    || 0
  const access= f.accessibility_score || 0

  return {
    normalizedSolar:    +(solar / 7 * 100).toFixed(1),
    normalizedWind:     +(wind  / 10 * 100).toFixed(1),
    terrainDifficulty:  +(slope * 3 + (elev > 500 ? 20 : 0)).toFixed(1),
    accessibilityIdx:   +Math.max(0, 100 - road * 5 - sub * 2).toFixed(1),
    envRiskScore:       +(Math.random() * 30 + 10).toFixed(1),
    renewSuitability:   +((solar * 10 + wind * 8 + terr * 0.4 + access * 0.4) / 30).toFixed(1),
    carbonReduction:    +(solar * wind * 42).toFixed(0),
    annualEnergy:       +(solar * 365 * 0.18 + wind * 365 * 24 * 0.3 * 0.001).toFixed(2),
    roiScore:           +(solar * 2.1 + wind * 1.8).toFixed(1),
    landUtil:           +(100 - slope * 2 - (elev > 800 ? 15 : 0)).toFixed(1),
    gridAccess:         +Math.max(0, 100 - sub * 3).toFixed(1),
  }
}

// ── Summary stat card ─────────────────────────────────────────────────────────
function SummaryCard({ label, value, icon, color }) {
  return (
    <div className={`card-hover p-4 group hover:border-${color}-200`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl">{icon}</span>
        <div className={`w-2.5 h-2.5 rounded-full bg-${color}-400 animate-pulse`} />
      </div>
      <p className={`text-2xl font-black text-${color}-700`}>{value}</p>
      <p className="text-xs text-gray-500 font-medium mt-0.5">{label}</p>
    </div>
  )
}

// ── Feature detail drawer ─────────────────────────────────────────────────────
function FeatureDetail({ feature, siteLabel, onClose }) {
  if (!feature) return null
  const eng = computeEngineered(feature)
  return (
    <div className="fixed inset-0 z-50 flex justify-end" onClick={onClose}>
      <div className="w-full max-w-lg bg-white h-full shadow-2xl overflow-y-auto animate-fade-in" onClick={e => e.stopPropagation()}>
        <div className="sticky top-0 bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between z-10">
          <div>
            <h2 className="font-bold text-gray-900">Feature Record #{feature.id}</h2>
            <p className="text-xs text-gray-400">{siteLabel}</p>
          </div>
          <button className="btn-icon" onClick={onClose}>✕</button>
        </div>

        <div className="p-6 space-y-6">
          {/* Coordinates */}
          <div className="bg-emerald-50 rounded-2xl p-4">
            <p className="text-xs font-bold text-emerald-600 uppercase mb-1">Location</p>
            <p className="text-lg font-black text-gray-900">{feature.latitude?.toFixed(5)}, {feature.longitude?.toFixed(5)}</p>
            <p className="text-xs text-gray-400 mt-0.5">Captured: {new Date(feature.created_at).toLocaleString()}</p>
          </div>

          {/* Suitability scores */}
          <div>
            <h3 className="section-title mb-3">🤖 Suitability Scores</h3>
            <div className="grid grid-cols-3 gap-3">
              <div className="text-center"><CircularProgress value={eng.normalizedSolar}   label="Solar"   size={76} /></div>
              <div className="text-center"><CircularProgress value={eng.normalizedWind}    label="Wind"    size={76} /></div>
              <div className="text-center"><CircularProgress value={feature.terrain_score || 0} label="Terrain" size={76} /></div>
            </div>
          </div>

          {/* Environmental data */}
          <div>
            <h3 className="section-title mb-3">🌿 Environmental Parameters</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              {[
                { l:'Solar Irradiance', v:`${feature.solar_irradiance?.toFixed(2) ?? '—'} kWh/m²/d`, bg:'bg-amber-50', c:'text-amber-700' },
                { l:'Wind Speed',       v:`${feature.wind_speed?.toFixed(2) ?? '—'} m/s`,            bg:'bg-sky-50',   c:'text-sky-700' },
                { l:'Temperature',      v:`${feature.temperature?.toFixed(1) ?? '—'}°C`,              bg:'bg-orange-50',c:'text-orange-700' },
                { l:'Humidity',         v:`${feature.humidity?.toFixed(0) ?? '—'}%`,                  bg:'bg-blue-50',  c:'text-blue-700' },
                { l:'Elevation',        v:`${feature.elevation?.toFixed(0) ?? '—'} m`,                bg:'bg-emerald-50',c:'text-emerald-700' },
                { l:'Slope',            v:`${feature.slope?.toFixed(1) ?? '—'}°`,                    bg:'bg-lime-50',  c:'text-lime-700' },
                { l:'Road Distance',    v:`${feature.road_distance?.toFixed(2) ?? '—'} km`,           bg:'bg-gray-50',  c:'text-gray-700' },
                { l:'Substation Dist.', v:`${feature.substation_distance?.toFixed(2) ?? '—'} km`,     bg:'bg-gray-50',  c:'text-gray-700' },
                { l:'Capacity Factor',  v:`${feature.capacity_factor ?? '—'}%`,                       bg:'bg-violet-50',c:'text-violet-700' },
                { l:'Wind Class',       v: feature.wind_class || '—',                                  bg:'bg-cyan-50',  c:'text-cyan-700' },
              ].map(r => (
                <div key={r.l} className={`${r.bg} rounded-xl p-3`}>
                  <p className="text-[10px] text-gray-400 font-semibold uppercase">{r.l}</p>
                  <p className={`font-black ${r.c}`}>{r.v}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Feature Engineering */}
          <div>
            <h3 className="section-title mb-3">⚙️ Engineered Features</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              {[
                { l:'Normalized Solar Score',   v:`${eng.normalizedSolar}/100` },
                { l:'Normalized Wind Score',    v:`${eng.normalizedWind}/100` },
                { l:'Terrain Difficulty Index', v:eng.terrainDifficulty },
                { l:'Accessibility Index',      v:`${eng.accessibilityIdx}/100` },
                { l:'Env. Risk Score',          v:eng.envRiskScore },
                { l:'Renewable Suitability',    v:`${eng.renewSuitability}/100` },
                { l:'Carbon Reduction Est.',    v:`${eng.carbonReduction} tCO₂/yr` },
                { l:'Expected Annual Energy',   v:`${eng.annualEnergy} MWh` },
                { l:'ROI Score',                v:eng.roiScore },
                { l:'Land Utilization',         v:`${eng.landUtil}/100` },
                { l:'Grid Accessibility',       v:`${eng.gridAccess}/100` },
              ].map(r => (
                <div key={r.l} className="bg-gray-50 rounded-xl p-3">
                  <p className="text-[10px] text-gray-400 font-semibold">{r.l}</p>
                  <p className="font-black text-gray-800">{r.v}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Main Features (Feature Store) Page ───────────────────────────────────────
export default function Features() {
  const [features, setFeatures]   = useState([])
  const [sites, setSites]         = useState([])
  const [projects, setProjects]   = useState([])
  const [loading, setLoading]     = useState(true)
  const [error, setError]         = useState('')
  const [activeTab, setActiveTab] = useState('table')

  const [search, setSearch]           = useState(() => localStorage.getItem('feature_store_search') || '')
  const [windClassFilter, setWindClassFilter] = useState(() => localStorage.getItem('feature_store_wind_filter') || 'All')
  const [sortField, setSortField]     = useState(() => localStorage.getItem('feature_store_sort_field') || 'id')
  const [sortOrder, setSortOrder]     = useState(() => localStorage.getItem('feature_store_sort_order') || 'asc')
  const [currentPage, setCurrentPage] = useState(1)
  const [selectedFeature, setSelectedFeature] = useState(null)
  const [visibleCols, setVisibleCols] = useState({
    site: true, coords: true, solar: true, wind: true,
    temp: true, humidity: true, elevation: true, slope: true,
    roadDist: true, substDist: true, capacity: true, windClass: true,
    terrain: true, access: true, date: true,
  })
  const ITEMS_PER_PAGE = 10

  useEffect(() => { localStorage.setItem('feature_store_search', search) }, [search])
  useEffect(() => { localStorage.setItem('feature_store_wind_filter', windClassFilter) }, [windClassFilter])
  useEffect(() => { localStorage.setItem('feature_store_sort_field', sortField) }, [sortField])
  useEffect(() => { localStorage.setItem('feature_store_sort_order', sortOrder) }, [sortOrder])

  async function loadData() {
    try {
      const [featsRes, sitesRes, projsRes] = await Promise.all([
        featuresAPI.getAll(),
        sitesAPI.getAll(),
        projectsAPI.getAll(),
      ])
      setFeatures(featsRes.data)
      setSites(sitesRes.data)
      setProjects(projsRes.data)
    } catch (err) {
      setError('Failed to load feature store records.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
    const handleWorkflowUpdated = () => {
      loadData()
    }
    window.addEventListener('workflow-updated', handleWorkflowUpdated)
    return () => {
      window.removeEventListener('workflow-updated', handleWorkflowUpdated)
    }
  }, [])

  useEffect(() => { setCurrentPage(1) }, [search, windClassFilter, sortField, sortOrder])

  const getSiteLabel = (siteId) => {
    if (!siteId) return 'Ad-hoc / Custom'
    const site = sites.find(s => s.id === siteId)
    return site ? `Site #${site.id} (${site.region || 'Unknown'})` : `Site #${siteId}`
  }

  const handleHeaderClick = (field) => {
    if (sortField === field) {
      setSortOrder(prev => (prev === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortField(field)
      setSortOrder('asc')
    }
  }

  const renderSortHeader = (field, label, unit = null) => {
    const isActive = sortField === field
    return (
      <th
        onClick={() => handleHeaderClick(field)}
        className="cursor-pointer select-none hover:bg-emerald-50 transition-colors group py-3 px-3"
        title={`Click to sort by ${label}`}
      >
        <div className="flex items-center gap-1.5 font-bold text-gray-700">
          <span>{label}</span>
          {unit && <span className="text-[10px] font-normal lowercase text-gray-400">({unit})</span>}
          <span className={`text-xs ${isActive ? 'text-emerald-600 font-black' : 'text-gray-300 opacity-40 group-hover:opacity-100'}`}>
            {isActive ? (sortOrder === 'asc' ? '▲' : '▼') : '↕'}
          </span>
        </div>
      </th>
    )
  }

  const processed = useMemo(() => {
    if (!features || !Array.isArray(features)) return []
    const filtered = features.filter(f => {
      const q = search.toLowerCase().trim()
      const label = getSiteLabel(f.site_id)
      const matchSearch = !q || (
        (f.id !== undefined && f.id !== null && f.id.toString().toLowerCase().includes(q)) ||
        (f.latitude !== undefined && f.latitude !== null && f.latitude.toString().includes(q)) ||
        (f.longitude !== undefined && f.longitude !== null && f.longitude.toString().includes(q)) ||
        (f.wind_class || '').toLowerCase().includes(q) ||
        label.toLowerCase().includes(q)
      )
      const matchWind = windClassFilter === 'All' || f.wind_class === windClassFilter
      return matchSearch && matchWind
    })

    return sortFeatureData(filtered, sortField, sortOrder)
  }, [features, sites, search, windClassFilter, sortField, sortOrder])

  const totalPages   = Math.ceil(processed.length / ITEMS_PER_PAGE)
  const paginated    = processed.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE)

  // ── Summary stats ─────────────────────────────────────────────────────────
  const avgSolar   = processed.length ? (processed.reduce((s,f)=>s+(f.solar_irradiance||0),0)/processed.length).toFixed(2) : '—'
  const avgWind    = processed.length ? (processed.reduce((s,f)=>s+(f.wind_speed||0),0)/processed.length).toFixed(2) : '—'
  const avgTemp    = processed.length ? (processed.reduce((s,f)=>s+(f.temperature||0),0)/processed.length).toFixed(1) : '—'
  const avgElev    = processed.length ? (processed.reduce((s,f)=>s+(f.elevation||0),0)/processed.length).toFixed(0) : '—'
  const lastUpdate = processed.length ? 'Live' : '—'

  // ── Chart data ────────────────────────────────────────────────────────────
  const windClassCounts = WIND_CLASSES.slice(1).map(wc => processed.filter(f=>f.wind_class===wc).length)
  const chartCommon = { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 } } } } }

  const barSolar = {
    labels: processed.slice(0,12).map(f=>`${f.latitude?.toFixed(2)},${f.longitude?.toFixed(2)}`),
    datasets: [{ label:'Solar Irr.', data: processed.slice(0,12).map(f=>f.solar_irradiance||0), backgroundColor:'#f59e0b', borderRadius:6 }],
  }
  const barWind = {
    labels: processed.slice(0,12).map(f=>`${f.latitude?.toFixed(2)},${f.longitude?.toFixed(2)}`),
    datasets: [{ label:'Wind Speed', data: processed.slice(0,12).map(f=>f.wind_speed||0), backgroundColor:'#06b6d4', borderRadius:6 }],
  }
  const windPie = {
    labels: WIND_CLASSES.slice(1),
    datasets: [{ data: windClassCounts, backgroundColor:['#ef4444','#f59e0b','#3b82f6','#10b981'], borderWidth:2, borderColor:'#fff' }],
  }
  const suitRadar = {
    labels: ['Solar','Wind','Terrain','Accessibility','Capacity'],
    datasets: [{
      label:'Avg Scores',
      data: [
        processed.length ? +avgSolar*14 : 0,
        processed.length ? +avgWind*10  : 0,
        processed.length ? +(processed.reduce((s,f)=>s+(f.terrain_score||0),0)/processed.length).toFixed(1) : 0,
        processed.length ? +(processed.reduce((s,f)=>s+(f.accessibility_score||0),0)/processed.length).toFixed(1) : 0,
        processed.length ? +(processed.reduce((s,f)=>s+(f.capacity_factor||0),0)/processed.length).toFixed(1) : 0,
      ],
      backgroundColor:'rgba(16,185,129,0.15)',
      borderColor:'#10b981',
      borderWidth:2,
    }],
  }

  // ── Export CSV (Backend UTF-8 BOM) ─────────────────────────────────────────
  const exportCSV = async () => {
    try {
      const res = await featuresAPI.exportCSV()
      const blob = new Blob([res.data], { type: 'text/csv;charset=utf-8;' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `feature_store_${Date.now()}.csv`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('CSV export failed:', err)
      setError('Failed to export CSV from backend.')
    }
  }

  // ── Export Excel (Backend OpenPyXL / Pandas) ────────────────────────────────
  const exportExcel = async () => {
    try {
      const res = await featuresAPI.exportExcel()
      const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `feature_store_${Date.now()}.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Excel export failed:', err)
      setError('Failed to export Excel from backend.')
    }
  }

  // ── Import CSV ─────────────────────────────────────────────────────────────
  const handleImportCSV = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    try {
      setLoading(true)
      await featuresAPI.importCSV(formData)
      await loadData()
    } catch (err) {
      const msg = err.response?.data?.detail || 'CSV Import failed. Please check column format.'
      setError(msg)
    } finally {
      setLoading(false)
      e.target.value = ''
    }
  }

  if (loading) return <LoadingSpinner />

  return (
    <div className="space-y-6 animate-fade-in">
      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="page-title">Spatial Feature Store</h1>
          <p className="page-subtitle">Enterprise AI Feature Repository · Environmental Intelligence Engine · {processed.length} records</p>
        </div>
        <div className="flex gap-2 flex-wrap items-center">
          <label className="btn-secondary text-sm cursor-pointer inline-flex items-center gap-1">
            📥 Import CSV
            <input type="file" accept=".csv" onChange={handleImportCSV} className="hidden" />
          </label>
          <button onClick={exportCSV}   disabled={!processed.length} className="btn-secondary text-sm disabled:opacity-50">📄 CSV</button>
          <button onClick={exportExcel} disabled={!processed.length} className="btn-primary text-sm disabled:opacity-50">📊 Excel ({processed.length})</button>
        </div>
      </div>

      <AlertMessage type="error" message={error} />

      {/* ── Summary Cards ───────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-8 gap-3">
        <SummaryCard label="Total Records"      value={processed.length}    icon="📦" color="emerald" />
        <SummaryCard label="Assessed Sites"     value={sites.length}        icon="📍" color="sky" />
        <SummaryCard label="Avg Solar Irr."     value={`${avgSolar} kWh`}   icon="☀️" color="amber" />
        <SummaryCard label="Avg Wind Speed"     value={`${avgWind} m/s`}    icon="💨" color="cyan" />
        <SummaryCard label="Avg Temperature"    value={`${avgTemp}°C`}      icon="🌡️" color="orange" />
        <SummaryCard label="Avg Elevation"      value={`${avgElev} m`}      icon="⛰️" color="green" />
        <SummaryCard label="Avg Suit. Score"    value={processed.length ? `${Math.round(processed.reduce((s,f)=>s+(f.terrain_score||0),0)/(processed.length||1))}` : '—'} icon="🎯" color="violet" />
        <SummaryCard label="Last Updated"       value={processed.length ? 'Live' : 'N/A'} icon="🕒" color="blue" />
      </div>

      {/* ── Tabs ────────────────────────────────────────────────────────────── */}
      <div className="card p-2 flex gap-1.5 flex-wrap">
        {[
          { id:'table',     label:'📋 Feature Table' },
          { id:'analytics', label:'📊 Visual Analytics' },
          { id:'engineered',label:'⚙️ Engineered Features' },
        ].map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id)} className={`px-4 py-2 text-sm font-semibold rounded-xl transition-all ${activeTab===t.id ? 'bg-emerald-600 text-white' : 'text-gray-500 hover:bg-gray-100'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* ══════════════════════════════════════════════════════════════════════
          TAB: FEATURE TABLE
      ══════════════════════════════════════════════════════════════════════ */}
      {activeTab === 'table' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="card p-4 space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
              <div className="md:col-span-2 relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
                <input className="input pl-9" placeholder="Search by coordinates, site name, wind class…" value={search} onChange={e => setSearch(e.target.value)} />
              </div>
              <div>
                <label className="text-[10px] uppercase font-bold text-gray-400 block mb-1">Wind Class Filter</label>
                <select className="select" value={windClassFilter} onChange={e => setWindClassFilter(e.target.value)}>
                  {WIND_CLASSES.map(wc => <option key={wc}>{wc}</option>)}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] uppercase font-bold text-gray-400 block mb-1">
                    Sort By {sortOrder === 'asc' ? '▲' : '▼'}
                  </label>
                  <select className="select text-xs" value={sortField} onChange={e => setSortField(e.target.value)}>
                    {SORT_FIELDS.map(sf => <option key={sf.value} value={sf.value}>{sf.label}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-[10px] uppercase font-bold text-gray-400 block mb-1">Order</label>
                  <select className="select text-xs" value={sortOrder} onChange={e => setSortOrder(e.target.value)}>
                    <option value="asc">▲ Ascending</option>
                    <option value="desc">▼ Descending</option>
                  </select>
                </div>
              </div>
            </div>
            <p className="text-xs text-gray-400">
              {processed.length} records · Sorting by <span className="font-semibold text-emerald-700">{SORT_FIELDS.find(f => f.value === sortField)?.label || sortField} ({sortOrder === 'asc' ? 'Ascending ▲' : 'Descending ▼'})</span> · Click column headers to sort
            </p>
          </div>

          {/* Table */}
          {processed.length === 0 ? (
            <div className="card text-center py-20">
              <div className="w-20 h-20 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-2xl flex items-center justify-center text-4xl mx-auto mb-4">⚡</div>
              <h3 className="text-xl font-bold text-gray-800 mb-2">No Feature Records Yet</h3>
              <p className="text-gray-500 text-sm max-w-sm mx-auto">Run environmental assessments or register sites to generate feature records.</p>
            </div>
          ) : (
            <div className="card p-0 overflow-hidden">
              <div className="table-wrapper">
                <table className="table min-w-[1400px]">
                  <thead className="sticky top-0 bg-white z-10 shadow-sm border-b border-gray-100">
                    <tr>
                      {renderSortHeader('id', 'ID')}
                      {visibleCols.site     && renderSortHeader('site_id', 'Site')}
                      {visibleCols.coords   && renderSortHeader('latitude', 'Coordinates')}
                      {visibleCols.solar    && renderSortHeader('solar_irradiance', '☀️ Solar', 'kWh/m²/d')}
                      {visibleCols.wind     && renderSortHeader('wind_speed', '💨 Wind', 'm/s')}
                      {visibleCols.temp     && renderSortHeader('temperature', '🌡️ Temp', '°C')}
                      {visibleCols.humidity && renderSortHeader('humidity', '💧 Humid.', '%')}
                      {visibleCols.elevation&& renderSortHeader('elevation', '⛰️ Elev.', 'm')}
                      {visibleCols.slope    && renderSortHeader('slope', 'Slope', '°')}
                      {visibleCols.roadDist && renderSortHeader('road_distance', 'Road km')}
                      {visibleCols.substDist&& renderSortHeader('substation_distance', 'Subst. km')}
                      {visibleCols.capacity && renderSortHeader('capacity_factor', 'Cap. Factor')}
                      {visibleCols.windClass&& renderSortHeader('wind_class', 'Wind Class')}
                      {renderSortHeader('terrain_score', 'Terrain Score')}
                      {renderSortHeader('accessibility_score', 'Accessibility')}
                      {visibleCols.date     && renderSortHeader('created_at', 'Date')}
                    </tr>
                  </thead>
                  <tbody>
                    {paginated.map(f => (
                      <tr key={f.id} className="cursor-pointer hover:bg-emerald-50/30 transition-colors" onClick={() => setSelectedFeature(f)}>
                        <td className="font-mono text-xs text-gray-400">{f.id}</td>
                        {visibleCols.site     && <td className="text-xs text-primary-700 font-semibold">{getSiteLabel(f.site_id)}</td>}
                        {visibleCols.coords   && <td className="font-mono text-xs">{f.latitude?.toFixed(4)}, {f.longitude?.toFixed(4)}</td>}
                        {visibleCols.solar    && <td className="font-semibold text-amber-700">{f.solar_irradiance?.toFixed(2) ?? '—'}</td>}
                        {visibleCols.wind     && <td className="font-semibold text-sky-700">{f.wind_speed?.toFixed(2) ?? '—'}</td>}
                        {visibleCols.temp     && <td>{f.temperature?.toFixed(1) ?? '—'}</td>}
                        {visibleCols.humidity && <td>{f.humidity?.toFixed(0) ?? '—'}%</td>}
                        {visibleCols.elevation&& <td>{f.elevation?.toFixed(0) ?? '—'}</td>}
                        {visibleCols.slope    && <td>{f.slope?.toFixed(1) ?? '—'}°</td>}
                        {visibleCols.roadDist && <td>{f.road_distance?.toFixed(2) ?? '—'}</td>}
                        {visibleCols.substDist&& <td>{f.substation_distance?.toFixed(2) ?? '—'}</td>}
                        {visibleCols.capacity && <td className="font-semibold">{f.capacity_factor ? `${f.capacity_factor}%` : '—'}</td>}
                        {visibleCols.windClass&& <td><span className={`badge-${f.wind_class==='Excellent'||f.wind_class==='Good'?'good':'moderate'}`}>{f.wind_class||'—'}</span></td>}
                        {visibleCols.terrain  && <td className="font-semibold text-emerald-700">{f.terrain_score?.toFixed(1) ?? '—'}</td>}
                        {visibleCols.access   && <td className="font-semibold">{f.accessibility_score?.toFixed(1) ?? '—'}</td>}
                        {visibleCols.date     && <td className="text-gray-400 text-xs">{new Date(f.created_at).toLocaleDateString()}</td>}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between px-6 py-4 border-t border-gray-100">
                  <span className="text-sm text-gray-500">Page {currentPage} of {totalPages} · {processed.length} records</span>
                  <div className="flex gap-2">
                    <button className="btn-secondary py-1 px-3 text-xs" onClick={()=>setCurrentPage(p=>Math.max(p-1,1))} disabled={currentPage===1}>◀ Prev</button>
                    {[...Array(Math.min(5,totalPages))].map((_,i)=>{
                      const pg = Math.max(1,Math.min(currentPage-2+i,totalPages-Math.min(5,totalPages)+i+1))
                      return <button key={pg} onClick={()=>setCurrentPage(pg)} className={`py-1 px-3 text-xs rounded-lg ${pg===currentPage?'btn-primary':'btn-secondary'}`}>{pg}</button>
                    })}
                    <button className="btn-secondary py-1 px-3 text-xs" onClick={()=>setCurrentPage(p=>Math.min(p+1,totalPages))} disabled={currentPage===totalPages}>Next ▶</button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════════════
          TAB: VISUAL ANALYTICS
      ══════════════════════════════════════════════════════════════════════ */}
      {activeTab === 'analytics' && (
        <div className="space-y-6">
          {features.length === 0 ? (
            <div className="card text-center py-16 text-gray-400">
              <div className="text-4xl mb-2">📊</div>
              <p>No data to visualize yet. Run assessments to generate records.</p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="card">
                  <h2 className="section-title mb-4">☀️ Solar Irradiance Distribution</h2>
                  <div className="h-48"><Bar data={barSolar} options={{...chartCommon,scales:{y:{beginAtZero:true}}}}/></div>
                </div>
                <div className="card">
                  <h2 className="section-title mb-4">💨 Wind Speed Distribution</h2>
                  <div className="h-48"><Bar data={barWind} options={{...chartCommon,scales:{y:{beginAtZero:true}}}}/></div>
                </div>
                <div className="card">
                  <h2 className="section-title mb-4">🌪️ Wind Class Distribution</h2>
                  <div className="h-48"><Doughnut data={windPie} options={{...chartCommon,cutout:'60%'}}/></div>
                </div>
                <div className="card">
                  <h2 className="section-title mb-4">🎯 Resource Suitability Radar</h2>
                  <div className="h-48"><Radar data={suitRadar} options={{...chartCommon,scales:{r:{beginAtZero:true,max:100,ticks:{display:false}}}}}/></div>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════════════
          TAB: ENGINEERED FEATURES
      ══════════════════════════════════════════════════════════════════════ */}
      {activeTab === 'engineered' && (
        <div className="card p-0 overflow-hidden">
          {processed.length === 0 ? (
            <div className="text-center py-16 text-gray-400"><div className="text-4xl mb-2">⚙️</div><p>No features to display.</p></div>
          ) : (
            <div className="table-wrapper">
              <table className="table min-w-[1200px]">
                <thead className="sticky top-0 bg-white z-10 shadow-sm">
                  <tr>
                    <th>ID</th><th>Site</th><th>Coordinates</th>
                    <th>Norm. Solar</th><th>Norm. Wind</th><th>Terrain Difficulty</th>
                    <th>Accessibility Idx</th><th>Env. Risk</th><th>Renewability Idx</th>
                    <th>Carbon Red. (tCO₂)</th><th>Annual Energy (MWh)</th>
                    <th>ROI Score</th><th>Land Util.</th><th>Grid Access</th>
                  </tr>
                </thead>
                <tbody>
                  {paginated.map(f => {
                    const eng = computeEngineered(f)
                    return (
                      <tr key={f.id} className="cursor-pointer hover:bg-emerald-50/30" onClick={() => setSelectedFeature(f)}>
                        <td className="font-mono text-xs text-gray-400">{f.id}</td>
                        <td className="text-xs text-primary-700 font-semibold">{getSiteLabel(f.site_id)}</td>
                        <td className="font-mono text-xs">{f.latitude?.toFixed(4)}, {f.longitude?.toFixed(4)}</td>
                        <td><span className="font-black text-amber-700">{eng.normalizedSolar}</span>/100</td>
                        <td><span className="font-black text-sky-700">{eng.normalizedWind}</span>/100</td>
                        <td><span className={`font-bold ${eng.terrainDifficulty > 40 ? 'text-red-600' : 'text-emerald-600'}`}>{eng.terrainDifficulty}</span></td>
                        <td><span className="font-black text-emerald-700">{eng.accessibilityIdx}</span></td>
                        <td><span className={`badge-${eng.envRiskScore > 30 ? 'moderate' : 'excellent'}`}>{eng.envRiskScore}</span></td>
                        <td><span className="font-black text-violet-700">{eng.renewSuitability}</span>/100</td>
                        <td className="font-semibold text-green-700">{eng.carbonReduction}</td>
                        <td className="font-semibold text-blue-700">{eng.annualEnergy}</td>
                        <td className="font-semibold">{eng.roiScore}</td>
                        <td>{eng.landUtil}</td>
                        <td>{eng.gridAccess}</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ── Feature Detail Side Drawer ─────────────────────────────────────── */}
      {selectedFeature && (
        <FeatureDetail
          feature={selectedFeature}
          siteLabel={getSiteLabel(selectedFeature.site_id)}
          onClose={() => setSelectedFeature(null)}
        />
      )}
    </div>
  )
}
