import { useEffect, useState } from 'react'
import { Zap, Shield, AlertTriangle } from 'lucide-react'
import { fetchRules } from '../api/endpoints'
import type { Rule }  from '../types'
import { CardSkeleton } from '../components/ui/LoadingSkeleton'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { SeverityBadge } from '../components/ui/Badge'

const WORKFLOW = ['Sense','Think','Act','Log']
const STEP_ICONS = ['📡','🧠','⚡','📋']
const STEP_DESCS = [
  'Raw sensor values are read from the dataset or API input.',
  'Rule engine evaluates each reading against configured thresholds.',
  'Decision engine applies priority logic and emits a final decision.',
  'All triggered rules and decisions are written to the audit log.',
]

export default function Automation() {
  const [rules, setRules]   = useState<Rule[]>([])
  const [meta, setMeta]     = useState<{ disclaimer: string; thresholds: Record<string, number> } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState<string | null>(null)

  useEffect(() => {
    fetchRules()
      .then(r => {
        const d = (r as { data: { rules: Rule[]; disclaimer: string; thresholds: Record<string, number> } }).data
        setRules(d.rules ?? [])
        setMeta({ disclaimer: d.disclaimer, thresholds: d.thresholds })
      })
      .catch(e => setError((e as Error).message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="space-y-3">{Array.from({length:4}).map((_,i)=><CardSkeleton key={i}/>)}</div>
  if (error)   return <ErrorMessage message={error}/>

  const criticalRules = rules.filter(r => r.severity === 'critical')
  const warningRules  = rules.filter(r => r.severity === 'warning')

  return (
    <div className="space-y-6">
      <div>
        <h2 className="page-title">Rule Engine — Automation</h2>
        <p className="page-subtitle">Sense → Think → Act → Log deterministic safety workflow</p>
      </div>

      {meta?.disclaimer && (
        <div className="rounded-lg border border-amber-700/30 bg-amber-900/10 p-3 text-xs text-amber-300">
          {meta.disclaimer}
        </div>
      )}

      {/* Workflow steps */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {WORKFLOW.map((step, i) => (
          <div key={step} className="card text-center">
            <div className="text-3xl mb-2">{STEP_ICONS[i]}</div>
            <p className="font-bold text-cyan-300 mb-1">{step}</p>
            <p className="text-xs text-[var(--text-secondary)]">{STEP_DESCS[i]}</p>
          </div>
        ))}
      </div>

      {/* Priority note */}
      <div className="card border-red-700/30 bg-red-900/10">
        <div className="flex items-start gap-3">
          <Shield className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0"/>
          <div>
            <p className="text-sm font-semibold text-red-300">Safety Layer Independence</p>
            <p className="text-xs text-[var(--text-secondary)] mt-1">
              The rule-based emergency-stop check runs before any ML prediction.
              A missing or failed ML model does NOT disable emergency-stop logic.
              Invalid inputs do NOT automatically yield SAFE.
              Safety-critical rules (marked ⚠) cannot be disabled through the dashboard.
            </p>
          </div>
        </div>
      </div>

      {/* Critical rules */}
      <div>
        <p className="section-title flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-red-400"/>
          Critical Safety Rules ({criticalRules.length})
        </p>
        <div className="table-container">
          <table className="table">
            <thead><tr><th>ID</th><th>Rule</th><th>Sensor</th><th>Threshold</th><th>Action</th><th>Safety</th><th>Triggers</th></tr></thead>
            <tbody>
              {criticalRules.map(r => (
                <tr key={r.id}>
                  <td className="font-mono text-xs text-[var(--text-secondary)]">{r.id}</td>
                  <td>
                    <p className="font-semibold text-sm">{r.name}</p>
                    <p className="text-xs text-[var(--text-secondary)]">{r.description}</p>
                  </td>
                  <td className="font-mono text-xs">{r.sensor}</td>
                  <td className="font-mono text-xs text-amber-400">{r.operator} {r.threshold}</td>
                  <td><span className="badge badge-critical text-[10px]">{r.action}</span></td>
                  <td>{r.safety_critical && <span className="text-amber-400 text-xs">⚠ Critical</span>}</td>
                  <td className="font-mono text-xs">{r.trigger_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Warning rules */}
      <div>
        <p className="section-title flex items-center gap-2">
          <Zap className="w-4 h-4 text-amber-400"/>
          Warning Rules ({warningRules.length})
        </p>
        <div className="table-container">
          <table className="table">
            <thead><tr><th>ID</th><th>Rule</th><th>Sensor</th><th>Threshold</th><th>Action</th><th>Triggers</th></tr></thead>
            <tbody>
              {warningRules.map(r => (
                <tr key={r.id}>
                  <td className="font-mono text-xs text-[var(--text-secondary)]">{r.id}</td>
                  <td>
                    <p className="font-semibold text-sm">{r.name}</p>
                    <p className="text-xs text-[var(--text-secondary)]">{r.description}</p>
                  </td>
                  <td className="font-mono text-xs">{r.sensor}</td>
                  <td className="font-mono text-xs text-amber-400">{r.operator} {r.threshold}</td>
                  <td><SeverityBadge severity={r.severity}/></td>
                  <td className="font-mono text-xs">{r.trigger_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
