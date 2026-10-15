import { useEffect, useState, useCallback } from 'react'
import {
  Cpu, CheckCircle, AlertTriangle, XCircle, Wrench,
  ShieldAlert, RefreshCw, TrendingUp, Clock
} from 'lucide-react'
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { KpiCard }         from '../components/ui/KpiCard'
import { CardSkeleton }    from '../components/ui/LoadingSkeleton'
import { ErrorMessage }    from '../components/ui/ErrorMessage'
import { EmptyState }      from '../components/ui/EmptyState'
import { DecisionBadge }   from '../components/ui/Badge'
import { fetchDashboardSummary, fetchDashboardTrends } from '../api/endpoints'
import type { DashboardSummary, DashboardTrends }      from '../types'
import { formatDateTime }  from '../utils/format'
import { format }          from 'date-fns'
import { useNavigate }     from 'react-router-dom'

const PIE_COLORS = { Normal: '#10b981', Warning: '#f59e0b', Failure: '#ef4444' }
const AREA_COLORS = { Normal: '#06b6d4', Warning: '#f59e0b', Failure: '#ef4444' }

function CriticalAlertBanner({ arms }: { arms: string[] }) {
  if (!arms.length) return null
  return (
    <div className="rounded-lg border border-red-600/50 bg-red-900/20 p-4 flex items-start gap-3">
      <XCircle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
      <div>
        <p className="text-sm font-semibold text-red-300">
          Emergency Stop Active — {arms.length} arm{arms.length > 1 ? 's' : ''} require immediate attention
        </p>
        <p className="text-xs text-red-400 mt-1">
          Affected: {arms.join(', ')}. Safety rule conditions exceeded. Do NOT override until inspection is complete.
        </p>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [summary, setSummary]   = useState<DashboardSummary | null>(null)
  const [trends,  setTrends]    = useState<DashboardTrends | null>(null)
  const [loading, setLoading]   = useState(true)
  const [error,   setError]     = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const load = useCallback(async () => {
    setLoading(true); setError(null)
    try {
      const [s, t] = await Promise.all([
        fetchDashboardSummary(),
        fetchDashboardTrends(),
      ])
      setSummary((s as { data: DashboardSummary }).data)
      setTrends((t as { data: DashboardTrends }).data)
      setLastUpdated(new Date())
    } catch (e: unknown) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  if (loading) return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => <CardSkeleton key={i} />)}
      </div>
    </div>
  )
  if (error) return <ErrorMessage message={error} onRetry={load} />

  const kpis  = summary?.kpis
  const dist  = kpis?.class_distribution ?? {}
  const emergencyArms = kpis?.emergency_arms ?? []

  const pieData = Object.entries(dist).map(([name, value]) => ({ name, value }))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="page-title">Industrial Command Center</h2>
          <p className="page-subtitle">
            Real-time machine health, predictive intelligence and operational safety
          </p>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          {lastUpdated && (
            <span className="text-xs text-[var(--text-secondary)] flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {format(lastUpdated, 'HH:mm:ss')}
            </span>
          )}
          <button className="btn-secondary text-xs" onClick={load}>
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh
          </button>
        </div>
      </div>

      {/* Status indicators */}
      <div className="flex items-center gap-4 text-xs text-[var(--text-secondary)]">
        <span className={`flex items-center gap-1.5 ${summary?.dataset_available ? 'text-emerald-400' : 'text-amber-400'}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${summary?.dataset_available ? 'bg-emerald-400' : 'bg-amber-400'}`} />
          {summary?.dataset_available ? 'Dataset loaded' : 'No dataset'}
        </span>
        <span className={`flex items-center gap-1.5 ${summary?.model_available ? 'text-emerald-400' : 'text-amber-400'}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${summary?.model_available ? 'bg-emerald-400' : 'bg-amber-400'}`} />
          {summary?.model_available ? 'ML model ready' : 'Model not trained'}
        </span>
        <span className="text-[var(--text-secondary)]">
          Data mode: Historical replay (not live hardware)
        </span>
      </div>

      {/* Emergency alert */}
      <CriticalAlertBanner arms={emergencyArms} />

      {/* KPIs */}
      {!summary?.dataset_available ? (
        <EmptyState
          title="No dataset available"
          message="Generate a dataset in the Data Lab to populate the dashboard with real metrics."
          action={<button className="btn-primary" onClick={() => navigate('/data-lab')}>Go to Data Lab</button>}
        />
      ) : (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <KpiCard label="Total Machines" value={kpis?.total_machines ?? 0}
              icon={Cpu} color="cyan"
              onClick={() => navigate('/fleet')} />
            <KpiCard label="Normal Operations" value={kpis?.normal_machines ?? 0}
              icon={CheckCircle} color="emerald"
              onClick={() => navigate('/fleet?status=SAFE')} />
            <KpiCard label="Warning Conditions" value={kpis?.warning_machines ?? 0}
              icon={AlertTriangle} color="amber"
              onClick={() => navigate('/fleet?status=WARNING')} />
            <KpiCard label="Emergency Stops" value={kpis?.emergency_stops ?? 0}
              icon={XCircle} color="red"
              onClick={() => navigate('/fleet?status=EMERGENCY_STOP')} />
            <KpiCard label="Predicted Failures" value={kpis?.predicted_maintenance ?? 0}
              icon={TrendingUp} color="purple"
              subtitle="Records with Failure wear label"
              onClick={() => navigate('/analytics')} />
            <KpiCard label="Integrity Alerts" value={kpis?.sensor_integrity_alerts ?? 0}
              icon={ShieldAlert} color="amber"
              onClick={() => navigate('/security')} />
            <KpiCard label="Open Maint. Cases" value={kpis?.maintenance_cases_open ?? 0}
              icon={Wrench} color="blue"
              onClick={() => navigate('/maintenance')} />
            <KpiCard label="Total Records" value={summary?.dataset_rows?.toLocaleString() ?? 0}
              icon={Cpu} color="cyan" />
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Trend area chart */}
            <div className="card lg:col-span-2">
              <p className="section-title">Condition Trend (Daily)</p>
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={trends?.trend_series ?? []} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={d => d.slice(5)} />
                  <YAxis tick={{ fontSize: 10 }} />
                  <Tooltip contentStyle={{ background: '#0d1526', border: '1px solid #1e2d4a', borderRadius: 6, fontSize: 12 }} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  {(['Normal','Warning','Failure'] as const).map(k => (
                    <Area key={k} type="monotone" dataKey={k} stackId="1"
                      stroke={AREA_COLORS[k]} fill={AREA_COLORS[k]} fillOpacity={0.3} />
                  ))}
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Pie chart */}
            <div className="card">
              <p className="section-title">Health Distribution</p>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={false} fontSize={11}>
                    {pieData.map((entry) => (
                      <Cell key={entry.name} fill={PIE_COLORS[entry.name as keyof typeof PIE_COLORS] ?? '#64748b'} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#0d1526', border: '1px solid #1e2d4a', borderRadius: 6, fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Sensor averages bar chart */}
          {trends?.sensor_avgs && trends.sensor_avgs.length > 0 && (
            <div className="card">
              <p className="section-title">Average Temperature by Arm</p>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={trends.sensor_avgs} margin={{ left: -20 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="arm_id" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: '#0d1526', border: '1px solid #1e2d4a', borderRadius: 6, fontSize: 12 }} />
                  <Bar dataKey="temperature" fill="#06b6d4" radius={[3,3,0,0]} name="Temp (°C)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Recent events table */}
          <div className="card">
            <div className="flex items-center justify-between mb-3">
              <p className="section-title mb-0">Recent Warning/Failure Events</p>
            </div>
            {trends?.recent_events && trends.recent_events.length > 0 ? (
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>Arm</th>
                      <th>Joint</th>
                      <th>Condition</th>
                      <th>Temp °C</th>
                      <th>Vibration</th>
                      <th>Torque Nm</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(trends.recent_events as typeof trends.recent_events).map((e, i) => (
                      <tr key={i}>
                        <td className="font-mono text-xs text-[var(--text-secondary)]">{formatDateTime(String(e.timestamp))}</td>
                        <td className="font-semibold">{e.arm_id}</td>
                        <td className="capitalize text-[var(--text-secondary)]">{e.joint}</td>
                        <td><DecisionBadge decision={e.wear_label} /></td>
                        <td className="font-mono">{Number(e.temperature).toFixed(1)}</td>
                        <td className="font-mono">{Number(e.vibration).toFixed(2)}</td>
                        <td className="font-mono">{Number(e.torque).toFixed(1)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-sm text-[var(--text-secondary)] py-4 text-center">No warning or failure events found.</p>
            )}
          </div>
        </>
      )}
    </div>
  )
}
