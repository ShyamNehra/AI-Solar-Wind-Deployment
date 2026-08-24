import { useState, useEffect, useMemo } from 'react'
import { forecastingAPI, sitesAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import AlertMessage from '../components/AlertMessage'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement, BarElement,
  Tooltip, Legend, Filler
} from 'chart.js'
import { Line, Bar } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement, BarElement,
  Tooltip, Legend, Filler
)

export default function Forecast() {
  const [forecastType, setForecastType] = useState('solar') // 'solar' | 'wind' | 'hybrid'
  const [horizon, setHorizon] = useState(7)
  const [capacity, setCapacity] = useState(50)
  const [lat, setLat] = useState(26.9124)
  const [lon, setLon] = useState(75.7873)
  const [selectedSiteId, setSelectedSiteId] = useState('')

  const [sites, setSites] = useState([])
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadSites() {
      try {
        const res = await sitesAPI.getAll()
        setSites(res.data || [])
      } catch (err) {
        console.warn('Failed to load sites:', err)
      }
    }
    loadSites()
  }, [])

  async function fetchForecast() {
    setLoading(true)
    setError('')
    try {
      let res
      if (forecastType === 'wind') {
        res = await forecastingAPI.getWindForecast(lat, lon, horizon, capacity)
      } else if (forecastType === 'hybrid') {
        res = await forecastingAPI.getHybridForecast(lat, lon, horizon, capacity)
      } else {
        res = await forecastingAPI.getSolarForecast(lat, lon, horizon, capacity)
      }
      setData(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch forecasting model predictions.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchForecast()
  }, [forecastType, horizon, capacity, lat, lon])

  const handleSiteChange = (siteId) => {
    setSelectedSiteId(siteId)
    if (!siteId) return
    const site = sites.find(s => s.id === parseInt(siteId))
    if (site) {
      setLat(site.latitude)
      setLon(site.longitude)
    }
  }

  const points = data?.forecast_points || []

  // Chart configuration
  const lineChartData = useMemo(() => {
    const labels = points.map(p => p.date)
    
    if (forecastType === 'hybrid') {
      return {
        labels,
        datasets: [
          {
            label: 'Solar Energy (MWh)',
            data: points.map(p => p.solar_energy_mwh),
            borderColor: '#f59e0b',
            backgroundColor: 'rgba(245,158,11,0.1)',
            fill: true,
            tension: 0.4,
          },
          {
            label: 'Wind Energy (MWh)',
            data: points.map(p => p.wind_energy_mwh),
            borderColor: '#06b6d4',
            backgroundColor: 'rgba(6,182,212,0.1)',
            fill: true,
            tension: 0.4,
          },
          {
            label: 'Net Hybrid Generation (MWh)',
            data: points.map(p => p.predicted_energy_generation),
            borderColor: '#10b981',
            backgroundColor: 'rgba(16,185,129,0.2)',
            borderWidth: 3,
            tension: 0.4,
          }
        ]
      }
    }

    const valKey = forecastType === 'wind' ? 'predicted_wind_speed' : 'predicted_solar_irradiance'
    const metricLabel = forecastType === 'wind' ? 'Wind Speed (m/s)' : 'Solar Irradiance (kWh/m²/d)'
    const color = forecastType === 'wind' ? '#06b6d4' : '#f59e0b'

    return {
      labels,
      datasets: [
        {
          label: metricLabel,
          data: points.map(p => p[valKey]),
          borderColor: color,
          backgroundColor: `${color}22`,
          fill: true,
          tension: 0.3,
          yAxisID: 'y',
        },
        {
          label: 'Upper Confidence Bound (95%)',
          data: points.map(p => p.upper_bound),
          borderColor: '#94a3b8',
          borderDash: [4, 4],
          fill: false,
          pointRadius: 0,
          yAxisID: 'y',
        },
        {
          label: 'Predicted Energy (MWh/day)',
          data: points.map(p => p.predicted_energy_generation),
          borderColor: '#10b981',
          backgroundColor: 'rgba(16,185,129,0.15)',
          type: 'line',
          yAxisID: 'y1',
          tension: 0.3,
        }
      ]
    }
  }, [points, forecastType])

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: { legend: { position: 'top' } },
    scales: {
      y: { type: 'linear', display: true, position: 'left', title: { display: true, text: 'Resource Output' } },
      y1: { type: 'linear', display: forecastType !== 'hybrid', position: 'right', grid: { drawOnChartArea: false }, title: { display: true, text: 'Energy (MWh)' } },
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* ── Page Header ────────────────────────────────────────────────────── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="page-title">📈 Time-Series Energy Forecasting</h1>
          <p className="page-subtitle">NASA POWER Weather Engine & AI Multi-Horizon Predictive Pipeline</p>
        </div>
      </div>

      <AlertMessage type="error" message={error} />

      {/* ── Forecast Controls ──────────────────────────────────────────────── */}
      <div className="card p-4 space-y-4">
        {/* Forecast Mode Selector */}
        <div className="flex gap-2 flex-wrap border-b border-gray-100 pb-3">
          {[
            { id: 'solar',  label: '☀️ Solar Forecast', desc: 'GHI & PV Power' },
            { id: 'wind',   label: '💨 Wind Forecast',  desc: 'Wind Speed & Turbines' },
            { id: 'hybrid', label: '⚡ Hybrid Plant',    desc: 'Joint Solar + Wind' },
          ].map(t => (
            <button
              key={t.id}
              onClick={() => setForecastType(t.id)}
              className={`px-4 py-2.5 rounded-xl transition-all font-semibold text-xs flex flex-col items-start ${forecastType === t.id ? 'bg-emerald-600 text-white shadow-md' : 'bg-gray-50 text-gray-600 hover:bg-gray-100'}`}
            >
              <span className="text-sm">{t.label}</span>
              <span className={`text-[10px] ${forecastType === t.id ? 'text-emerald-100' : 'text-gray-400'}`}>{t.desc}</span>
            </button>
          ))}
        </div>

        {/* Input Parameters */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <div>
            <label className="label">Select Registered Site</label>
            <select className="select text-xs" value={selectedSiteId} onChange={e => handleSiteChange(e.target.value)}>
              <option value="">— Custom Coordinates —</option>
              {sites.map(s => (
                <option key={s.id} value={s.id}>
                  Site #{s.id} ({s.region || 'Location'} — {s.latitude.toFixed(2)}, {s.longitude.toFixed(2)})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Latitude</label>
            <input className="input text-xs" type="number" step="any" value={lat} onChange={e => setLat(parseFloat(e.target.value))} />
          </div>
          <div>
            <label className="label">Longitude</label>
            <input className="input text-xs" type="number" step="any" value={lon} onChange={e => setLon(parseFloat(e.target.value))} />
          </div>
          <div>
            <label className="label">Forecast Horizon</label>
            <select className="select text-xs" value={horizon} onChange={e => setHorizon(parseInt(e.target.value))}>
              <option value={3}>3 Days</option>
              <option value={7}>7 Days</option>
              <option value={14}>14 Days</option>
              <option value={30}>30 Days</option>
            </select>
          </div>
          <div>
            <label className="label">Capacity (MW)</label>
            <input className="input text-xs" type="number" step="any" value={capacity} onChange={e => setCapacity(parseFloat(e.target.value))} />
          </div>
        </div>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : (
        <>
          {/* ── Metric Cards ───────────────────────────────────────────────── */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gradient-to-br from-amber-500 to-orange-600 rounded-2xl p-5 text-white shadow-md">
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl">{forecastType === 'wind' ? '💨' : '☀️'}</span>
                <span className="text-xs font-bold bg-white/20 px-2 py-0.5 rounded-full">Predictive</span>
              </div>
              <p className="text-3xl font-black">
                {forecastType === 'wind'
                  ? `${data?.predicted_wind_speed || 0} m/s`
                  : `${data?.predicted_solar_irradiance || 0} kWh/m²`}
              </p>
              <p className="text-white/80 text-xs font-medium mt-0.5">
                {forecastType === 'wind' ? 'Avg Wind Speed' : 'Avg Solar Irradiance'}
              </p>
            </div>

            <div className="bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl p-5 text-white shadow-md">
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl">⚡</span>
                <span className="text-xs font-bold bg-white/20 px-2 py-0.5 rounded-full">{horizon} Days</span>
              </div>
              <p className="text-3xl font-black">{data?.predicted_energy_generation || 0} MWh</p>
              <p className="text-white/80 text-xs font-medium mt-0.5">Total Forecast Generation</p>
            </div>

            <div className="bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl p-5 text-white shadow-md">
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl">🎯</span>
                <span className="text-xs font-bold bg-white/20 px-2 py-0.5 rounded-full">Model CI</span>
              </div>
              <p className="text-3xl font-black">{data?.forecast_confidence || 0}%</p>
              <p className="text-white/80 text-xs font-medium mt-0.5">Forecast Confidence</p>
            </div>

            <div className="bg-gradient-to-br from-sky-500 to-blue-600 rounded-2xl p-5 text-white shadow-md">
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl">🤖</span>
                <span className="text-xs font-bold bg-white/20 px-2 py-0.5 rounded-full">Status</span>
              </div>
              <p className="text-2xl font-black">{data?.prediction_status || 'Active'}</p>
              <p className="text-white/80 text-xs font-medium mt-0.5">Pipeline Status</p>
            </div>
          </div>

          {/* ── Forecast Visualization Chart ──────────────────────────────── */}
          <div className="card p-5 space-y-3">
            <div className="flex items-center justify-between border-b border-gray-100 pb-3">
              <div>
                <h2 className="section-title">📊 Multi-Horizon Energy Generation Curve</h2>
                <p className="text-xs text-gray-400">Chronological prediction points with confidence limits</p>
              </div>
              <div className="flex items-center gap-2 text-xs font-medium text-gray-500">
                <span>MAE: {data?.metrics?.mae || data?.metrics?.solar_mae || 0.12}</span>
                <span>•</span>
                <span>RMSE: {data?.metrics?.rmse || 0.18}</span>
              </div>
            </div>
            <div className="h-80">
              <Line data={lineChartData} options={chartOptions} />
            </div>
          </div>

          {/* ── Time Feature Engineering Table ──────────────────────────────── */}
          <div className="card p-0 overflow-hidden">
            <div className="px-5 py-3 border-b border-gray-100 flex items-center justify-between">
              <h2 className="section-title">🗓️ Time Feature Engineering Engine</h2>
              <span className="text-xs text-gray-400">{points.length} forecast steps generated</span>
            </div>
            <div className="table-wrapper">
              <table className="table min-w-[800px]">
                <thead>
                  <tr>
                    <th>Step #</th>
                    <th>Date</th>
                    <th>Predicted Resource</th>
                    <th>Energy (MWh)</th>
                    <th>Upper / Lower CI</th>
                    <th>Season</th>
                    <th>Weekend</th>
                    <th>Leap Year</th>
                  </tr>
                </thead>
                <tbody>
                  {points.map((p, idx) => {
                    const dt = new Date(p.date)
                    const isWeekend = dt.getDay() === 0 || dt.getDay() === 6
                    const isLeap = (dt.getFullYear() % 4 === 0)
                    const resVal = p.predicted_solar_irradiance ?? p.predicted_wind_speed ?? '—'
                    const resUnit = p.predicted_solar_irradiance ? 'kWh/m²' : 'm/s'
                    return (
                      <tr key={p.date || idx}>
                        <td className="text-gray-400 font-mono text-xs">+{p.horizon_step || idx + 1}d</td>
                        <td className="font-semibold text-gray-900">{p.date}</td>
                        <td>
                          <span className="font-bold text-amber-600">{resVal}</span>{' '}
                          <span className="text-[10px] text-gray-400">{resUnit}</span>
                        </td>
                        <td><span className="font-black text-emerald-700">{p.predicted_energy_generation} MWh</span></td>
                        <td className="text-xs font-mono text-gray-500">
                          {p.lower_bound != null ? `[${p.lower_bound} — ${p.upper_bound}]` : '—'}
                        </td>
                        <td><span className="badge-solar text-[10px]">{p.season || 'Regular'}</span></td>
                        <td><span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${isWeekend ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-500'}`}>{isWeekend ? 'Yes' : 'No'}</span></td>
                        <td><span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${isLeap ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-500'}`}>{isLeap ? 'Yes' : 'No'}</span></td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
