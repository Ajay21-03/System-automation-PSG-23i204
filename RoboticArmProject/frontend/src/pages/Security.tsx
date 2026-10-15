import { useEffect, useState, useCallback } from 'react'
import { Shield, Play, RefreshCw } from 'lucide-react'
import { fetchSecurityEvents, postSecuritySimulate } from '../api/endpoints'
import type { SecurityEvent } from '../types'
import { CardSkeleton } from '../components/ui/LoadingSkeleton'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { EmptyState }   from '../components/ui/EmptyState'
import { SeverityBadge } from '../components/ui/Badge'
import { useToast }     from '../store/toast'
import { formatDateTime } from '../utils/format'

export default function Security() {
  const { show }          = useToast()
  const [events, setEvents]     = useState<SecurityEvent[]>([])
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState<string | null>(null)
  const [simResult, setSimResult] = useState<Record<string, unknown> | null>(null)
  const [simLoading, setSimLoading] = useState(false)

  const load = useCallback(async () => {
    setLoading(true); setError(null)
    try {
      const res = await fetchSecurityEvents({ limit: 200 }) as { data: { events: SecurityEvent[] } }
      setEvents(res.data?.events ?? [])
    } catch (e: unknown) { setError((e as Error).message) }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  const runSimulation = async () => {
    setSimLoading(true)
    try {
      const res = await postSecuritySimulate({ arm_id: 'ARM-001', joint: 'shoulder' }) as { data: Record<string, unknown> }
      setSimResult(res.data)
      show('Simulation complete', 'success')
      load()
    } catch (e: unknown) { show((e as Error).message, 'error') }
    finally { setSimLoading(false) }
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="page-title">Security & Sensor Integrity</h2>
          <p className="page-subtitle">Physical-range, abrupt-change, cross-sensor, and constant-value detection</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary text-xs" onClick={load}><RefreshCw className="w-3.5 h-3.5"/>Refresh</button>
          <button className="btn-primary text-xs" onClick={runSimulation} disabled={simLoading}>
            <Play className="w-3.5 h-3.5"/>
            {simLoading ? 'Running...' : 'Run Spoofing Demo'}
          </button>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="rounded-lg border border-amber-700/30 bg-amber-900/10 p-3 text-xs text-amber-300">
        <strong>Security limitation disclosure:</strong> These checks detect basic anomalies.
        Slow/gradual spoofing within plausible ranges cannot be detected.
        Coordinated multi-sensor spoofing may evade cross-sensor checks.
        This is not a cryptographic or hardware-authenticated system.
      </div>

      {/* Simulation result */}
      {simResult && (
        <div className="card border-cyan-700/30">
          <p className="section-title">{simResult.scenario as string}</p>
          <p className="text-xs text-amber-400 mb-3">{simResult.disclaimer as string}</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-xs font-semibold text-[var(--text-secondary)] mb-2">Original (genuine failure)</p>
              <div className="bg-[var(--bg-secondary)] rounded p-3 text-xs font-mono space-y-1">
                {Object.entries(simResult.original_reading as Record<string, unknown>).map(([k, v]) => (
                  <div key={k} className="flex justify-between">
                    <span className="text-[var(--text-secondary)]">{k}</span>
                    <span className="text-[var(--text-primary)]">{String(v)}</span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <p className="text-xs font-semibold text-red-400 mb-2">Spoofed (attacker modified torque)</p>
              <div className="bg-red-900/10 border border-red-700/30 rounded p-3 text-xs font-mono space-y-1">
                {Object.entries(simResult.spoofed_reading as Record<string, unknown>).map(([k, v]) => {
                  const orig = (simResult.original_reading as Record<string, unknown>)[k]
                  const changed = v !== orig
                  return (
                    <div key={k} className="flex justify-between">
                      <span className="text-[var(--text-secondary)]">{k}</span>
                      <span className={changed ? 'text-red-400 font-bold' : 'text-[var(--text-primary)]'}>{String(v)}</span>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
          <div className="mb-3">
            <p className="text-xs font-semibold text-emerald-400 mb-1">Attacks caught by:</p>
            {(simResult.attacks_caught_by as string[])?.length > 0 ? (
              <ul className="space-y-1">
                {(simResult.attacks_caught_by as string[]).map((r, i) => (
                  <li key={i} className="text-xs text-[var(--text-secondary)] flex gap-2">
                    <span className="text-emerald-400">✓</span>{r}
                  </li>
                ))}
              </ul>
            ) : <p className="text-xs text-amber-400">No attacks detected by current rules.</p>}
          </div>
          <div>
            <p className="text-xs font-semibold text-[var(--text-secondary)] mb-1">Limitations:</p>
            <ul className="space-y-1">
              {(simResult.limitations as string[]).map((l, i) => (
                <li key={i} className="text-xs text-[var(--text-secondary)] flex gap-2">
                  <span className="text-amber-400">⚠</span>{l}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Events table */}
      {loading ? <div className="space-y-2">{Array.from({length:4}).map((_,i)=><CardSkeleton key={i}/>)}</div>
      : error   ? <ErrorMessage message={error} onRetry={load}/>
      : events.length === 0 ? (
        <EmptyState icon={Shield} title="No integrity events"
          message="Run the spoofing simulation or scan-dataset to generate events."/>
      ) : (
        <div className="card">
          <p className="section-title">{events.length} integrity events</p>
          <div className="table-container">
            <table className="table">
              <thead><tr>
                <th>Time</th><th>Machine</th><th>Sensor</th>
                <th>Severity</th><th>Reason</th><th>Value</th>
              </tr></thead>
              <tbody>
                {events.map(e => (
                  <tr key={e.id}>
                    <td className="font-mono text-xs">{formatDateTime(e.detected_at)}</td>
                    <td className="font-semibold">{e.machine_id}</td>
                    <td className="text-[var(--text-secondary)]">{e.sensor}</td>
                    <td><SeverityBadge severity={e.severity}/></td>
                    <td className="text-xs max-w-xs">{e.reason}</td>
                    <td className="font-mono text-xs">{e.value}</td>
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
