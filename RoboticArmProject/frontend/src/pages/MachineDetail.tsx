import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ChevronRight, RefreshCw } from 'lucide-react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend
} from 'recharts'
import { fetchMachine }    from '../api/endpoints'
import type { MachineDetail } from '../types'
import { CardSkeleton }    from '../components/ui/LoadingSkeleton'
import { ErrorMessage }    from '../components/ui/ErrorMessage'
import { DecisionBadge, IntegrityBadge } from '../components/ui/Badge'
import { formatDateTime, formatNum } from '../utils/format'
import { DECISION_BG }     from '../utils/severity'
import type { DecisionKey } from '../utils/severity'

const SENSORS = ['temperature','vibration','torque','rpm','current','pressure'] as const
const SENSOR_UNITS: Record<string, string> = {
  temperature: '°C', vibration: 'mm/s', torque: 'Nm',
  rpm: 'RPM', current: 'A', pressure: 'bar'
}

function JointCard({ name, data }: { name: string; data: Record<string, unknown> }) {
  const badge = (data.wear_label as string) === 'Normal' ? 'badge-safe'
    : (data.wear_label as string) === 'Warning' ? 'badge-warning' : 'badge-critical'
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <p className="font-semibold capitalize text-[var(--text-primary)]">{name}</p>
        <span className={`badge ${badge}`}>{data.wear_label as string}</span>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs">
        {SENSORS.slice(0,4).map(s => (
          <div key={s} className="bg-[var(--bg-secondary)] rounded p-2">
            <p className="text-[var(--text-secondary)]">{s}</p>
            <p className="font-mono font-semibold">{formatNum(data[s] as number, 2)} {SENSOR_UNITS[s]}</p>
          </div>
        ))}
      </div>
      <p className="text-[10px] text-[var(--text-secondary)] mt-2">{data.record_count as number} records</p>
    </div>
  )
}

// Simple SVG robotic arm illustration
function ArmSvg({ joints }: { joints: Record<string, unknown> }) {
  const color = (j: string) => {
    const wl = (joints[j] as Record<string, string>)?.wear_label
    if (wl === 'Failure') return '#ef4444'
    if (wl === 'Warning') return '#f59e0b'
    return '#10b981'
  }
  return (
    <svg viewBox="0 0 200 240" className="w-full max-w-[160px] mx-auto" aria-label="Robotic arm joint health diagram">
      {/* Base */}
      <rect x="75" y="210" width="50" height="20" rx="4" fill="#1e2d4a"/>
      <rect x="90" y="200" width="20" height="15" rx="2" fill="#1e2d4a"/>
      {/* Shoulder joint */}
      <circle cx="100" cy="190" r="14" fill={color('shoulder')} fillOpacity={0.8} stroke="#0d1526" strokeWidth="2"/>
      <text x="100" y="195" textAnchor="middle" fontSize="7" fill="white" fontWeight="600">SH</text>
      {/* Upper arm */}
      <line x1="100" y1="176" x2="100" y2="130" stroke="#334155" strokeWidth="8" strokeLinecap="round"/>
      {/* Elbow joint */}
      <circle cx="100" cy="120" r="12" fill={color('elbow')} fillOpacity={0.8} stroke="#0d1526" strokeWidth="2"/>
      <text x="100" y="125" textAnchor="middle" fontSize="7" fill="white" fontWeight="600">EL</text>
      {/* Lower arm */}
      <line x1="112" y1="114" x2="140" y2="80" stroke="#334155" strokeWidth="7" strokeLinecap="round"/>
      {/* Wrist joint */}
      <circle cx="148" cy="68" r="10" fill={color('wrist')} fillOpacity={0.8} stroke="#0d1526" strokeWidth="2"/>
      <text x="148" y="73" textAnchor="middle" fontSize="7" fill="white" fontWeight="600">WR</text>
      {/* End effector */}
      <line x1="156" y1="62" x2="170" y2="45" stroke="#475569" strokeWidth="5" strokeLinecap="round"/>
      <circle cx="172" cy="42" r="4" fill="#64748b"/>
      {/* Legend */}
      <circle cx="20" cy="20" r="5" fill="#10b981"/>
      <text x="29" y="25" fontSize="8" fill="#94a3b8">Normal</text>
      <circle cx="20" cy="36" r="5" fill="#f59e0b"/>
      <text x="29" y="41" fontSize="8" fill="#94a3b8">Warning</text>
      <circle cx="20" cy="52" r="5" fill="#ef4444"/>
      <text x="29" y="57" fontSize="8" fill="#94a3b8">Failure</text>
      <text x="100" y="235" textAnchor="middle" fontSize="7" fill="#475569">Simulated representation</text>
    </svg>
  )
}

export default function MachineDetailPage() {
  const { armId }           = useParams<{ armId: string }>()
  const [detail, setDetail] = useState<MachineDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState<string | null>(null)

  const load = async () => {
    if (!armId) return
    setLoading(true); setError(null)
    try {
      const res = await fetchMachine(armId) as { data: MachineDetail }
      setDetail(res.data)
    } catch (e: unknown) { setError((e as Error).message) }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [armId])

  if (loading) return <div className="space-y-4">{Array.from({length:4}).map((_,i)=><CardSkeleton key={i}/>)}</div>
  if (error)   return <ErrorMessage message={error} onRetry={load} />
  if (!detail) return null

  const decKey = detail.decision as DecisionKey
  const bgCls  = DECISION_BG[decKey] ?? ''

  return (
    <div className="space-y-5">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-xs text-[var(--text-secondary)]">
        <Link to="/fleet" className="hover:text-[var(--text-primary)]">Fleet</Link>
        <ChevronRight className="w-3 h-3"/>
        <span className="text-[var(--text-primary)]">{detail.arm_id}</span>
      </nav>

      {/* Header */}
      <div className={`card border ${bgCls}`}>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold">{detail.arm_id}</h2>
            <p className="text-sm text-[var(--text-secondary)] mt-1">{detail.reason}</p>
          </div>
          <div className="flex items-center gap-2">
            <DecisionBadge decision={detail.decision} />
            <button className="btn-secondary text-xs" onClick={load}><RefreshCw className="w-3.5 h-3.5"/></button>
          </div>
        </div>
        {detail.evidence.length > 0 && (
          <ul className="mt-3 space-y-1">
            {detail.evidence.map((e, i) => (
              <li key={i} className="text-xs text-[var(--text-secondary)] flex items-start gap-2">
                <span className="text-cyan-400 mt-0.5">›</span>{e}
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Joint cards + Arm SVG */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div className="card flex items-center justify-center p-6">
          <ArmSvg joints={detail.joints} />
        </div>
        {Object.entries(detail.joints).map(([joint, data]) => (
          <JointCard key={joint} name={joint} data={data as unknown as Record<string, unknown>} />
        ))}
      </div>

      {/* ML result */}
      {detail.ml_result && !('error' in detail.ml_result) && (
        <div className="card">
          <p className="section-title">ML Prediction</p>
          <div className="flex flex-wrap gap-4 items-start">
            <div>
              <p className="text-xs text-[var(--text-secondary)]">Predicted class</p>
              <p className="text-lg font-bold mt-1">{detail.ml_result.predicted_class}</p>
            </div>
            {Object.entries(detail.ml_result.probabilities).map(([cls, prob]) => (
              <div key={cls} className="min-w-[100px]">
                <p className="text-xs text-[var(--text-secondary)]">{cls}</p>
                <div className="flex items-center gap-2 mt-1">
                  <div className="h-2 rounded-full bg-[var(--bg-secondary)] flex-1">
                    <div className="h-full rounded-full bg-cyan-500" style={{ width: `${(prob as number) * 100}%` }} />
                  </div>
                  <span className="text-xs font-mono">{((prob as number) * 100).toFixed(1)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sensor history chart */}
      {detail.history.length > 0 && (
        <div className="card">
          <p className="section-title">Sensor History (last {detail.history.length} readings)</p>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={detail.history} margin={{ left: -20, right: 10 }}>
              <CartesianGrid strokeDasharray="3 3"/>
              <XAxis dataKey="timestamp" tick={{ fontSize: 9 }} tickFormatter={d => d?.slice(11,16)} />
              <YAxis tick={{ fontSize: 9 }}/>
              <Tooltip contentStyle={{ background:'#0d1526', border:'1px solid #1e2d4a', borderRadius:6, fontSize:11 }} labelFormatter={l => l?.slice(0,16)}/>
              <Legend wrapperStyle={{ fontSize: 11 }}/>
              <Line dataKey="temperature" stroke="#f59e0b" dot={false} strokeWidth={1.5} name="Temp °C"/>
              <Line dataKey="vibration"   stroke="#ef4444" dot={false} strokeWidth={1.5} name="Vibration"/>
              <Line dataKey="torque"      stroke="#06b6d4" dot={false} strokeWidth={1.5} name="Torque Nm"/>
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Recent events */}
      {detail.recent_events.length > 0 && (
        <div className="card">
          <p className="section-title">Recent Warning/Failure Events</p>
          <div className="table-container">
            <table className="table">
              <thead><tr><th>Time</th><th>Joint</th><th>Condition</th><th>Temp</th><th>Vibration</th><th>Torque</th></tr></thead>
              <tbody>
                {detail.recent_events.map((e, i) => (
                  <tr key={i}>
                    <td className="font-mono text-xs">{formatDateTime(String(e.timestamp))}</td>
                    <td className="capitalize">{e.joint}</td>
                    <td><DecisionBadge decision={e.wear_label}/></td>
                    <td className="font-mono text-xs">{Number(e.temperature).toFixed(1)}</td>
                    <td className="font-mono text-xs">{Number(e.vibration).toFixed(2)}</td>
                    <td className="font-mono text-xs">{Number(e.torque).toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
