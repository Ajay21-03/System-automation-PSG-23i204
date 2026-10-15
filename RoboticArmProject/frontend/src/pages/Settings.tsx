import { useEffect, useState } from 'react'
import { CheckCircle, XCircle, RefreshCw, Sun, Moon } from 'lucide-react'
import { fetchSystemStatus } from '../api/endpoints'
import type { SystemStatus } from '../types'
import { CardSkeleton } from '../components/ui/LoadingSkeleton'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { useTheme }     from '../store/theme'

function StatusRow({ label, ok, value }: { label: string; ok: boolean; value?: string }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-[var(--border)] last:border-0">
      <div className="flex items-center gap-2">
        {ok ? <CheckCircle className="w-4 h-4 text-emerald-400"/> : <XCircle className="w-4 h-4 text-red-400"/>}
        <span className="text-sm text-[var(--text-primary)]">{label}</span>
      </div>
      {value && <span className="text-xs font-mono text-[var(--text-secondary)] max-w-xs truncate">{value}</span>}
    </div>
  )
}

export default function Settings() {
  const { theme, toggle } = useTheme()
  const [status, setStatus] = useState<SystemStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState<string | null>(null)

  const load = () => {
    setLoading(true)
    fetchSystemStatus()
      .then(r => setStatus((r as { data: SystemStatus }).data))
      .catch(e => setError((e as Error).message))
      .finally(() => setLoading(false))
  }
  useEffect(load, [])

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h2 className="page-title">Settings & System Health</h2>
        <p className="page-subtitle">Application preferences and backend status</p>
      </div>

      {/* Display preferences */}
      <div className="card">
        <p className="section-title">Display Preferences</p>
        <div className="flex items-center justify-between py-2">
          <div>
            <p className="text-sm text-[var(--text-primary)]">Theme</p>
            <p className="text-xs text-[var(--text-secondary)]">Choose between dark and light interface</p>
          </div>
          <button onClick={toggle}
            className="flex items-center gap-2 px-3 py-2 rounded-md border border-[var(--border)] bg-[var(--bg-secondary)] text-sm hover:bg-[var(--bg-panel)] transition-colors">
            {theme === 'dark'
              ? <><Moon className="w-4 h-4 text-cyan-400"/> Dark</>
              : <><Sun  className="w-4 h-4 text-amber-400"/> Light</>}
          </button>
        </div>
      </div>

      {/* System health */}
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <p className="section-title mb-0">System Health</p>
          <button className="btn-secondary text-xs" onClick={load}><RefreshCw className="w-3.5 h-3.5"/>Refresh</button>
        </div>
        {loading ? <CardSkeleton/>
        : error   ? <ErrorMessage message={error} onRetry={load}/>
        : status && (
          <div>
            <StatusRow label="Dataset file"    ok={status.dataset_exists} value={status.dataset_path}/>
            <StatusRow label="ML model file"   ok={status.model_exists}   value={status.model_path}/>
            <StatusRow label="ML model loaded" ok={status.model_loaded}/>
            <StatusRow label="Database"        ok={status.db_exists}/>
            <div className="flex items-center justify-between py-2 border-b border-[var(--border)]">
              <span className="text-sm text-[var(--text-primary)]">Application Version</span>
              <span className="text-xs font-mono text-cyan-400">{status.version}</span>
            </div>
          </div>
        )}
      </div>

      {/* Thresholds */}
      {status?.thresholds && (
        <div className="card">
          <p className="section-title">Configured Thresholds</p>
          <p className="text-xs text-amber-400 italic mb-3">
            Simulation assumptions only. NOT certified industrial safety limits.
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {Object.entries(status.thresholds)
              .filter(([k]) => !k.includes('min') && !k.includes('max'))
              .map(([k, v]) => (
                <div key={k} className="bg-[var(--bg-secondary)] rounded p-2">
                  <p className="text-[10px] text-[var(--text-secondary)] uppercase">{k.replace(/_/g,' ')}</p>
                  <p className="font-mono text-sm font-semibold text-[var(--text-primary)]">{v}</p>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* About */}
      <div className="card">
        <p className="section-title">About</p>
        <div className="space-y-1 text-sm text-[var(--text-secondary)]">
          <p><strong className="text-[var(--text-primary)]">Project:</strong> Industrial Intelligence Command Center</p>
          <p><strong className="text-[var(--text-primary)]">Course:</strong> 23IF02 — System Automation</p>
          <p><strong className="text-[var(--text-primary)]">Stack:</strong> React + Vite + TypeScript · Flask · Random Forest</p>
          <p><strong className="text-[var(--text-primary)]">Data:</strong> Synthetic simulation data — academic use only</p>
        </div>
      </div>
    </div>
  )
}
