import { useEffect, useState, useCallback } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Search, RefreshCw, Grid3X3, List, ChevronRight } from 'lucide-react'
import { fetchFleet }       from '../api/endpoints'
import type { Machine }     from '../types'
import { CardSkeleton }     from '../components/ui/LoadingSkeleton'
import { ErrorMessage }     from '../components/ui/ErrorMessage'
import { EmptyState }       from '../components/ui/EmptyState'
import { DecisionBadge, IntegrityBadge } from '../components/ui/Badge'
import { formatDateTime }   from '../utils/format'

const STATUS_ORDER = ['EMERGENCY_STOP','WARNING','SCHEDULE_MAINTENANCE','SAFE']

function MachineCard({ m, onClick }: { m: Machine; onClick: () => void }) {
  const borderColor: Record<string, string> = {
    EMERGENCY_STOP: 'border-red-600/60 bg-red-900/10',
    WARNING:        'border-amber-600/40',
    SCHEDULE_MAINTENANCE: 'border-amber-700/30',
    SAFE:           'border-[var(--border)]',
  }
  return (
    <div
      className={`card cursor-pointer hover:border-cyan-600/50 transition-colors ${borderColor[m.status] ?? ''}`}
      onClick={onClick}
      role="button" tabIndex={0}
      onKeyDown={e => e.key === 'Enter' && onClick()}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="font-semibold text-[var(--text-primary)]">{m.arm_id}</p>
          <p className="text-xs text-[var(--text-secondary)] capitalize">{m.joint} joint · {m.record_count} records</p>
        </div>
        <DecisionBadge decision={m.status} />
      </div>
      <div className="grid grid-cols-3 gap-2 text-xs mb-3">
        {[
          ['Temp', `${m.temperature?.toFixed(1)} °C`],
          ['Vibr', `${m.vibration?.toFixed(2)} mm/s`],
          ['Torque', `${m.torque?.toFixed(1)} Nm`],
        ].map(([k, v]) => (
          <div key={k} className="bg-[var(--bg-secondary)] rounded p-2">
            <p className="text-[var(--text-secondary)]">{k}</p>
            <p className="font-mono font-semibold text-[var(--text-primary)]">{v}</p>
          </div>
        ))}
      </div>
      <div className="flex items-center justify-between">
        <IntegrityBadge status={m.sensor_integrity} />
        <span className="text-[10px] text-[var(--text-secondary)]">
          {formatDateTime(m.last_timestamp)}
        </span>
      </div>
    </div>
  )
}

function MachineRow({ m, onClick }: { m: Machine; onClick: () => void }) {
  return (
    <tr className="cursor-pointer" onClick={onClick}>
      <td className="font-semibold">{m.arm_id}</td>
      <td><DecisionBadge decision={m.status} /></td>
      <td className="capitalize text-[var(--text-secondary)]">{m.joint}</td>
      <td className="font-mono text-xs">{m.temperature?.toFixed(1)}°C</td>
      <td className="font-mono text-xs">{m.vibration?.toFixed(2)}</td>
      <td className="font-mono text-xs">{m.torque?.toFixed(1)}</td>
      <td><IntegrityBadge status={m.sensor_integrity} /></td>
      <td className="text-xs text-[var(--text-secondary)]">{formatDateTime(m.last_timestamp)}</td>
      <td><ChevronRight className="w-4 h-4 text-[var(--text-secondary)]" /></td>
    </tr>
  )
}

export default function Fleet() {
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const [machines, setMachines] = useState<Machine[]>([])
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState<string | null>(null)
  const [search, setSearch]     = useState('')
  const [statusFilter, setStatusFilter] = useState(params.get('status') ?? '')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  const load = useCallback(async () => {
    setLoading(true); setError(null)
    try {
      const res = await fetchFleet() as { data: { machines: Machine[] } }
      const sorted = [...(res.data?.machines ?? [])].sort(
        (a, b) => STATUS_ORDER.indexOf(a.status) - STATUS_ORDER.indexOf(b.status)
      )
      setMachines(sorted)
    } catch (e: unknown) { setError((e as Error).message) }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  const filtered = machines.filter(m => {
    const q = search.toUpperCase()
    const matchSearch = !q || m.arm_id.includes(q)
    const matchStatus = !statusFilter || m.status === statusFilter
    return matchSearch && matchStatus
  })

  if (loading) return <div className="grid grid-cols-2 md:grid-cols-3 gap-4">{Array.from({length:6}).map((_,i)=><CardSkeleton key={i}/>)}</div>
  if (error)   return <ErrorMessage message={error} onRetry={load} />

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <div className="page-header mb-0">
          <h2 className="page-title">Machine Fleet</h2>
          <p className="page-subtitle">{machines.length} machines monitored</p>
        </div>
        <button className="btn-secondary text-xs" onClick={load}><RefreshCw className="w-3.5 h-3.5"/>Refresh</button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[var(--text-secondary)]"/>
          <input className="input pl-8 w-44 h-8 text-xs" placeholder="Search arm ID..."
            value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="select h-8 text-xs w-44"
          value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
          <option value="">All statuses</option>
          <option value="SAFE">Safe</option>
          <option value="WARNING">Warning</option>
          <option value="SCHEDULE_MAINTENANCE">Maintenance</option>
          <option value="EMERGENCY_STOP">Emergency Stop</option>
        </select>
        <div className="flex rounded-md border border-[var(--border)] overflow-hidden">
          <button className={`px-2 py-1.5 text-xs transition-colors ${viewMode==='grid'?'bg-cyan-900/40 text-cyan-300':'text-[var(--text-secondary)] hover:bg-[var(--bg-panel)]'}`}
            onClick={() => setViewMode('grid')}><Grid3X3 className="w-3.5 h-3.5"/></button>
          <button className={`px-2 py-1.5 text-xs transition-colors ${viewMode==='list'?'bg-cyan-900/40 text-cyan-300':'text-[var(--text-secondary)] hover:bg-[var(--bg-panel)]'}`}
            onClick={() => setViewMode('list')}><List className="w-3.5 h-3.5"/></button>
        </div>
      </div>

      {filtered.length === 0 ? (
        <EmptyState title="No machines found" message="Try adjusting your search or filter." />
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filtered.map(m => (
            <MachineCard key={m.arm_id} m={m}
              onClick={() => navigate(`/fleet/${m.arm_id}`)} />
          ))}
        </div>
      ) : (
        <div className="table-container">
          <table className="table">
            <thead><tr>
              <th>Arm ID</th><th>Status</th><th>Joint</th>
              <th>Temp</th><th>Vibration</th><th>Torque</th>
              <th>Integrity</th><th>Last Reading</th><th></th>
            </tr></thead>
            <tbody>
              {filtered.map(m => (
                <MachineRow key={m.arm_id} m={m}
                  onClick={() => navigate(`/fleet/${m.arm_id}`)} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
