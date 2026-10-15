import { useEffect, useState, useCallback } from 'react'
import { Send, RefreshCw, Download } from 'lucide-react'
import { fetchMaintenanceLogs, postMaintenanceLog, fetchAnalyzeLogFile } from '../api/endpoints'
import type { MaintenanceLogEntry } from '../types'
import { CardSkeleton } from '../components/ui/LoadingSkeleton'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { EmptyState }   from '../components/ui/EmptyState'
import { SeverityBadge } from '../components/ui/Badge'
import { useToast }     from '../store/toast'
import { formatDateTime } from '../utils/format'
import { FileText }     from 'lucide-react'

export default function MaintenanceLogs() {
  const { show }           = useToast()
  const [entries, setEntries] = useState<MaintenanceLogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState<string | null>(null)
  const [text, setText]       = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [severityFilter, setSeverityFilter] = useState('')
  const [relevantFilter, setRelevantFilter] = useState('')

  const load = useCallback(async () => {
    setLoading(true); setError(null)
    try {
      const res = await fetchMaintenanceLogs({
        severity:  severityFilter  || undefined,
        relevant:  relevantFilter  || undefined,
        limit: 100
      }) as { data: { entries: MaintenanceLogEntry[] } }
      setEntries(res.data?.entries ?? [])
    } catch (e: unknown) { setError((e as Error).message) }
    finally { setLoading(false) }
  }, [severityFilter, relevantFilter])

  useEffect(() => { load() }, [load])

  const handleSubmit = async () => {
    if (!text.trim()) { show('Please enter a note', 'warning'); return }
    setSubmitting(true)
    try {
      await postMaintenanceLog({ text })
      show('Note analyzed and saved', 'success')
      setText('')
      load()
    } catch (e: unknown) { show((e as Error).message, 'error') }
    finally { setSubmitting(false) }
  }

  const handleLoadFile = async () => {
    try {
      await fetchAnalyzeLogFile()
      show('Log file analyzed and imported', 'success')
      load()
    } catch (e: unknown) { show((e as Error).message, 'error') }
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="page-title">Maintenance Log Intelligence</h2>
          <p className="page-subtitle">Keyword-based NLP analysis with negation handling</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary text-xs" onClick={handleLoadFile}>
            <Download className="w-3.5 h-3.5"/>Import Log File
          </button>
          <button className="btn-secondary text-xs" onClick={load}>
            <RefreshCw className="w-3.5 h-3.5"/>Refresh
          </button>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="rounded-lg border border-amber-700/30 bg-amber-900/10 p-3 text-xs text-amber-300">
        Keyword-based analysis only — NOT a verified technician diagnosis. Results are indicative.
        Negation detection is basic and may not catch all cases.
      </div>

      {/* Submit form */}
      <div className="card">
        <p className="section-title">Add Maintenance Note</p>
        <textarea
          className="input mb-3 resize-none h-24 text-sm"
          placeholder="e.g. ARM-001 shoulder joint showing grinding noise and elevated vibration..."
          value={text} onChange={e => setText(e.target.value)} maxLength={2000}/>
        <div className="flex items-center justify-between">
          <span className="text-xs text-[var(--text-secondary)]">{text.length}/2000</span>
          <button className="btn-primary text-xs" onClick={handleSubmit} disabled={submitting}>
            <Send className="w-3.5 h-3.5"/>
            {submitting ? 'Analyzing...' : 'Analyze & Save'}
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <select className="select h-8 text-xs w-36" value={severityFilter} onChange={e => setSeverityFilter(e.target.value)}>
          <option value="">All severities</option>
          <option value="critical">Critical</option>
          <option value="warning">Warning</option>
          <option value="info">Info</option>
        </select>
        <select className="select h-8 text-xs w-36" value={relevantFilter} onChange={e => setRelevantFilter(e.target.value)}>
          <option value="">All notes</option>
          <option value="true">Relevant only</option>
          <option value="false">Non-relevant only</option>
        </select>
      </div>

      {loading ? <div className="space-y-2">{Array.from({length:5}).map((_,i)=><CardSkeleton key={i}/>)}</div>
      : error   ? <ErrorMessage message={error} onRetry={load}/>
      : entries.length === 0 ? (
        <EmptyState icon={FileText} title="No log entries"
          message="Import the maintenance log file or add a note above." />
      ) : (
        <div className="space-y-3">
          {entries.map(e => {
            const terms = (() => { try { return JSON.parse(e.detected_terms) } catch { return [] } })()
            return (
              <div key={e.id} className={`card ${e.relevant ? '' : 'opacity-75'}`}>
                <div className="flex items-start justify-between gap-4 mb-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <SeverityBadge severity={e.severity}/>
                    {e.relevant ? (
                      <span className="badge badge-warning text-[10px]">Relevant</span>
                    ) : (
                      <span className="badge badge-info text-[10px]">Administrative</span>
                    )}
                    {e.machine_id && <span className="text-xs font-semibold text-[var(--text-primary)]">{e.machine_id}</span>}
                    {e.joint && <span className="text-xs text-[var(--text-secondary)] capitalize">{e.joint}</span>}
                  </div>
                  <span className="text-xs text-[var(--text-secondary)] whitespace-nowrap">{formatDateTime(e.created_at)}</span>
                </div>
                <p className="text-sm text-[var(--text-primary)] mb-2">"{e.text}"</p>
                {terms.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-2">
                    {(terms as string[]).map((t: string) => (
                      <span key={t} className="badge badge-warning text-[10px]">{t}</span>
                    ))}
                  </div>
                )}
                <p className="text-xs text-[var(--text-secondary)] italic">{e.explanation}</p>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
