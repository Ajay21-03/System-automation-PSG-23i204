import { useEffect, useState, useCallback } from 'react'
import { RefreshCw, Download } from 'lucide-react'
import { fetchLogs } from '../api/endpoints'
import type { AuditEvent } from '../types'
import { CardSkeleton } from '../components/ui/LoadingSkeleton'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { EmptyState }   from '../components/ui/EmptyState'
import { SeverityBadge, DecisionBadge } from '../components/ui/Badge'
import { formatDateTime } from '../utils/format'
import { ScrollText }   from 'lucide-react'

const PAGE_SIZE = 50

export default function Logs() {
  const [events, setEvents]     = useState<AuditEvent[]>([])
  const [total, setTotal]       = useState(0)
  const [page, setPage]         = useState(0)
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState<string | null>(null)
  const [typeFilter, setTypeFilter] = useState('')

  const load = useCallback(async () => {
    setLoading(true); setError(null)
    try {
      const res = await fetchLogs({ limit: PAGE_SIZE, offset: page * PAGE_SIZE }) as {
        data: { events: AuditEvent[]; total: number }
      }
      setEvents(res.data?.events ?? [])
      setTotal(res.data?.total ?? 0)
    } catch (e: unknown) { setError((e as Error).message) }
    finally { setLoading(false) }
  }, [page])

  useEffect(() => { load() }, [load])

  const filtered = typeFilter
    ? events.filter(e => e.event_type.includes(typeFilter))
    : events

  const eventTypes = [...new Set(events.map(e => e.event_type))]

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="page-title">Event & Audit Logs</h2>
          <p className="page-subtitle">{total} total events</p>
        </div>
        <div className="flex gap-2">
          <a href="/api/logs/export" target="_blank" rel="noreferrer" className="btn-secondary text-xs">
            <Download className="w-3.5 h-3.5"/>Export CSV
          </a>
          <button className="btn-secondary text-xs" onClick={load}><RefreshCw className="w-3.5 h-3.5"/>Refresh</button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <select className="select h-8 text-xs w-44" value={typeFilter} onChange={e => setTypeFilter(e.target.value)}>
          <option value="">All event types</option>
          {eventTypes.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>

      {loading ? <div className="space-y-2">{Array.from({length:6}).map((_,i)=><CardSkeleton key={i}/>)}</div>
      : error   ? <ErrorMessage message={error} onRetry={load}/>
      : filtered.length === 0 ? (
        <EmptyState icon={ScrollText} title="No audit events yet"
          message="Events are recorded as you use the application."/>
      ) : (
        <>
          <div className="table-container">
            <table className="table">
              <thead><tr>
                <th>Timestamp</th><th>Type</th><th>Machine</th>
                <th>Severity</th><th>Source</th><th>Description</th><th>Decision</th>
              </tr></thead>
              <tbody>
                {filtered.map((e, i) => (
                  <tr key={i}>
                    <td className="font-mono text-xs whitespace-nowrap">{formatDateTime(e.timestamp)}</td>
                    <td className="font-mono text-xs text-cyan-400">{e.event_type}</td>
                    <td className="font-semibold">{e.machine_id ?? '—'}</td>
                    <td><SeverityBadge severity={e.severity}/></td>
                    <td className="text-xs text-[var(--text-secondary)]">{e.source}</td>
                    <td className="text-xs max-w-xs truncate">{e.description}</td>
                    <td>{e.decision ? <DecisionBadge decision={e.decision}/> : <span className="text-[var(--text-secondary)]">—</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between text-xs text-[var(--text-secondary)]">
            <span>Showing {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, total)} of {total}</span>
            <div className="flex gap-2">
              <button className="btn-secondary text-xs h-7 px-2" onClick={() => setPage(p=>Math.max(0,p-1))} disabled={page===0}>Previous</button>
              <button className="btn-secondary text-xs h-7 px-2" onClick={() => setPage(p=>p+1)} disabled={(page+1)*PAGE_SIZE >= total}>Next</button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
