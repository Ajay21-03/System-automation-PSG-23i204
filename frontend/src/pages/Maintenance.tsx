import { useEffect, useState, useCallback } from 'react'
import { RefreshCw, Plus, Filter } from 'lucide-react'
import { fetchMaintenance, postMaintenance, patchMaintenance } from '../api/endpoints'
import type { MaintenanceCase, MaintStatus } from '../types'
import { CardSkeleton } from '../components/ui/LoadingSkeleton'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { EmptyState }   from '../components/ui/EmptyState'
import { SeverityBadge } from '../components/ui/Badge'
import { useToast }     from '../store/toast'
import { formatDateTime } from '../utils/format'
import { Wrench }       from 'lucide-react'

const STATUS_OPTIONS: MaintStatus[] = ['open','acknowledged','scheduled','resolved']
const PRIORITY_COLORS: Record<string, string> = {
  high:   'text-red-400', medium: 'text-amber-400', low: 'text-cyan-400'
}

export default function MaintenancePage() {
  const { show }        = useToast()
  const [cases, setCases]     = useState<MaintenanceCase[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [showForm, setShowForm]         = useState(false)
  const [form, setForm] = useState({ machine_id:'', decision:'SCHEDULE_MAINTENANCE', severity:'warning', description:'', priority:'medium' })

  const load = useCallback(async () => {
    setLoading(true); setError(null)
    try {
      const res = await fetchMaintenance({ status: statusFilter || undefined, limit: 100 }) as { data: { cases: MaintenanceCase[] } }
      setCases(res.data?.cases ?? [])
    } catch (e: unknown) { setError((e as Error).message) }
    finally { setLoading(false) }
  }, [statusFilter])

  useEffect(() => { load() }, [load])

  const handleCreate = async () => {
    if (!form.machine_id) { show('Machine ID is required', 'error'); return }
    try {
      await postMaintenance(form)
      show('Maintenance case created', 'success')
      setShowForm(false)
      setForm({ machine_id:'', decision:'SCHEDULE_MAINTENANCE', severity:'warning', description:'', priority:'medium' })
      load()
    } catch (e: unknown) { show((e as Error).message, 'error') }
  }

  const handleStatusChange = async (id: number, status: MaintStatus) => {
    try {
      await patchMaintenance(id, { status })
      show(`Case updated to ${status}`, 'success')
      load()
    } catch (e: unknown) { show((e as Error).message, 'error') }
  }

  if (loading) return <div className="space-y-3">{Array.from({length:5}).map((_,i)=><CardSkeleton key={i}/>)}</div>
  if (error)   return <ErrorMessage message={error} onRetry={load}/>

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="page-title">Maintenance Intelligence</h2>
          <p className="page-subtitle">{cases.length} cases</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary text-xs" onClick={load}><RefreshCw className="w-3.5 h-3.5"/>Refresh</button>
          <button className="btn-primary text-xs"  onClick={() => setShowForm(s=>!s)}><Plus className="w-3.5 h-3.5"/>New Case</button>
        </div>
      </div>

      {/* Create form */}
      {showForm && (
        <div className="card border-cyan-700/30">
          <p className="section-title">New Maintenance Case</p>
          <div className="grid grid-cols-2 gap-3 mb-3">
            {[['machine_id','Machine ID'],['description','Description (optional)']].map(([k,l]) => (
              <div key={k}>
                <label className="text-xs text-[var(--text-secondary)]">{l}</label>
                <input className="input mt-1 h-8 text-xs" value={form[k as keyof typeof form]}
                  onChange={e => setForm(f => ({ ...f, [k]: e.target.value }))}/>
              </div>
            ))}
            <div>
              <label className="text-xs text-[var(--text-secondary)]">Decision</label>
              <select className="select mt-1 h-8 text-xs" value={form.decision}
                onChange={e => setForm(f => ({ ...f, decision: e.target.value }))}>
                <option>SCHEDULE_MAINTENANCE</option>
                <option>MONITOR</option>
                <option>SAFE</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-[var(--text-secondary)]">Priority</label>
              <select className="select mt-1 h-8 text-xs" value={form.priority}
                onChange={e => setForm(f => ({ ...f, priority: e.target.value }))}>
                <option>high</option><option>medium</option><option>low</option>
              </select>
            </div>
          </div>
          <div className="flex gap-2">
            <button className="btn-primary text-xs" onClick={handleCreate}>Create</button>
            <button className="btn-secondary text-xs" onClick={() => setShowForm(false)}>Cancel</button>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex items-center gap-3">
        <Filter className="w-4 h-4 text-[var(--text-secondary)]"/>
        <div className="flex gap-2 flex-wrap">
          {['','open','acknowledged','scheduled','resolved'].map(s => (
            <button key={s} onClick={() => setStatusFilter(s)}
              className={`px-3 py-1 rounded-full text-xs border transition-colors ${statusFilter === s ? 'bg-cyan-900/40 border-cyan-700/40 text-cyan-300' : 'border-[var(--border)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]'}`}>
              {s || 'All'}
            </button>
          ))}
        </div>
      </div>

      {cases.length === 0 ? (
        <EmptyState icon={Wrench} title="No maintenance cases"
          message="Cases are created automatically when the decision engine detects issues, or you can create one manually."/>
      ) : (
        <div className="table-container">
          <table className="table">
            <thead><tr>
              <th>ID</th><th>Machine</th><th>Joint</th><th>Decision</th>
              <th>Severity</th><th>Priority</th><th>Status</th>
              <th>Created</th><th>Actions</th>
            </tr></thead>
            <tbody>
              {cases.map(c => (
                <tr key={c.id}>
                  <td className="font-mono text-xs text-[var(--text-secondary)]">#{c.id}</td>
                  <td className="font-semibold">{c.machine_id}</td>
                  <td className="capitalize text-[var(--text-secondary)]">{c.joint ?? '—'}</td>
                  <td><span className="text-xs font-mono">{c.decision}</span></td>
                  <td><SeverityBadge severity={c.severity}/></td>
                  <td className={`text-xs font-semibold ${PRIORITY_COLORS[c.priority] ?? ''}`}>{c.priority}</td>
                  <td>
                    <select className="select h-7 text-xs py-0" value={c.status}
                      onChange={e => handleStatusChange(c.id, e.target.value as MaintStatus)}>
                      {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </td>
                  <td className="text-xs text-[var(--text-secondary)]">{formatDateTime(c.created_at)}</td>
                  <td className="text-xs text-[var(--text-secondary)] max-w-xs truncate">{c.description || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
