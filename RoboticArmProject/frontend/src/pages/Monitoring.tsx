import { useEffect, useState, useCallback, useRef } from 'react'
import { RefreshCw, Play, Pause } from 'lucide-react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts'
import { fetchReadings } from '../api/endpoints'
import type { SensorReading } from '../types'
import { CardSkeleton } from '../components/ui/LoadingSkeleton'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { IntegrityBadge } from '../components/ui/Badge'

const ARM_IDS = ['ARM-001','ARM-002','ARM-003','ARM-004','ARM-005']
const JOINTS  = ['shoulder','elbow','wrist']
const THRESHOLDS: Record<string, { warning: number; critical: number; unit: string }> = {
  temperature: { warning: 75,   critical: 95,   unit: '°C'   },
  vibration:   { warning: 4.5,  critical: 7.0,  unit: 'mm/s' },
  torque:      { warning: 85,   critical: 110,  unit: 'Nm'   },
  rpm:         { warning: 2800, critical: 3400, unit: 'RPM'  },
  current:     { warning: 12,   critical: 16,   unit: 'A'    },
  pressure:    { warning: 7.5,  critical: 9.5,  unit: 'bar'  },
}
const SENSOR_COLORS: Record<string, string> = {
  temperature: '#f59e0b', vibration: '#ef4444', torque: '#06b6d4',
  rpm: '#a78bfa', current: '#34d399', pressure: '#f472b6'
}

function SensorMini({ label, value, unit, flag }: { label:string; value:number; unit:string; flag:string }) {
  const color = flag === 'critical' ? 'text-red-400' : flag === 'warning' ? 'text-amber-400' : 'text-emerald-400'
  return (
    <div className="card text-center">
      <p className="text-[10px] text-[var(--text-secondary)] uppercase tracking-wide mb-1">{label}</p>
      <p className={`text-xl font-mono font-bold ${color}`}>{value?.toFixed?.(2) ?? '—'}</p>
      <p className="text-[10px] text-[var(--text-secondary)]">{unit}</p>
    </div>
  )
}

export default function Monitoring() {
  const [readings, setReadings] = useState<SensorReading[]>([])
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState<string | null>(null)
  const [armId, setArmId]       = useState('')
  const [joint, setJoint]       = useState('')
  const [auto, setAuto]         = useState(false)
  const [mode, setMode]         = useState<string>('')
  const intervalRef             = useRef<number | null>(null)

  const load = useCallback(async () => {
    setLoading(true); setError(null)
    try {
      const res = await fetchReadings({ arm_id: armId || undefined, joint: joint || undefined, limit: 100 }) as {
        data: { readings: SensorReading[]; mode: string; mode_label: string }
      }
      setReadings(res.data?.readings ?? [])
      setMode(res.data?.mode_label ?? '')
    } catch (e: unknown) { setError((e as Error).message) }
    finally { setLoading(false) }
  }, [armId, joint])

  useEffect(() => { load() }, [load])

  useEffect(() => {
    if (auto) {
      intervalRef.current = setInterval(load, 5000) as unknown as number
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }
    return () => { if (intervalRef.current) clearInterval(intervalRef.current) }
  }, [auto, load])

  const latest = readings[readings.length - 1]

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="page-title">Sensor Monitoring</h2>
          <p className="page-subtitle text-amber-400/80 text-xs mt-1">
            {mode || 'Historical data replay — not live hardware acquisition'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button className={`btn-secondary text-xs ${auto ? 'text-cyan-400 border-cyan-700' : ''}`}
            onClick={() => setAuto(a => !a)}>
            {auto ? <Pause className="w-3.5 h-3.5"/> : <Play className="w-3.5 h-3.5"/>}
            {auto ? 'Stop auto-refresh' : 'Auto refresh (5s)'}
          </button>
          <button className="btn-secondary text-xs" onClick={load}>
            <RefreshCw className="w-3.5 h-3.5"/>Refresh
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <select className="select h-8 text-xs w-36" value={armId} onChange={e => setArmId(e.target.value)}>
          <option value="">All Arms</option>
          {ARM_IDS.map(a => <option key={a} value={a}>{a}</option>)}
        </select>
        <select className="select h-8 text-xs w-36" value={joint} onChange={e => setJoint(e.target.value)}>
          <option value="">All Joints</option>
          {JOINTS.map(j => <option key={j} value={j} className="capitalize">{j}</option>)}
        </select>
      </div>

      {loading ? <div className="grid grid-cols-3 md:grid-cols-6 gap-3">{Array.from({length:6}).map((_,i)=><CardSkeleton key={i}/>)}</div>
      : error   ? <ErrorMessage message={error} onRetry={load}/>
      : (
        <>
          {/* Latest reading cards */}
          {latest && (
            <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
              {Object.entries(THRESHOLDS).map(([sensor, meta]) => {
                const val  = latest[sensor as keyof SensorReading] as number
                const flag = latest.threshold_flags?.[sensor] ?? 'normal'
                return <SensorMini key={sensor} label={sensor} value={val} unit={meta.unit} flag={flag}/>
              })}
            </div>
          )}

          {/* Integrity + arm info */}
          {latest && (
            <div className="flex items-center gap-4 text-xs text-[var(--text-secondary)]">
              <span>Arm: <strong className="text-[var(--text-primary)]">{latest.arm_id}</strong></span>
              <span>Joint: <strong className="text-[var(--text-primary)] capitalize">{latest.joint}</strong></span>
              <IntegrityBadge status={latest.sensor_integrity}/>
            </div>
          )}

          {/* Time series chart */}
          {readings.length > 0 && (
            <div className="card">
              <p className="section-title">Sensor Time Series ({readings.length} readings)</p>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={readings} margin={{ left: -20, right: 10 }}>
                  <CartesianGrid strokeDasharray="3 3"/>
                  <XAxis dataKey="timestamp" tick={{ fontSize: 9 }} tickFormatter={d => d?.slice(11,16)}/>
                  <YAxis tick={{ fontSize: 9 }}/>
                  <Tooltip contentStyle={{ background:'#0d1526', border:'1px solid #1e2d4a', borderRadius:6, fontSize:11 }}
                    labelFormatter={l => l?.slice(0,16)}/>
                  {Object.entries(SENSOR_COLORS).map(([s, c]) => (
                    <Line key={s} dataKey={s} stroke={c} dot={false} strokeWidth={1.5} name={s}/>
                  ))}
                  <ReferenceLine y={THRESHOLDS.temperature.warning} stroke="#f59e0b" strokeDasharray="4 4" opacity={0.5}/>
                  <ReferenceLine y={THRESHOLDS.vibration.critical}  stroke="#ef4444" strokeDasharray="4 4" opacity={0.5}/>
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}
    </div>
  )
}
