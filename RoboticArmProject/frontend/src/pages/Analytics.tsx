import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { fetchAnalyticsMetrics, postDecisionEvaluate } from '../api/endpoints'
import type { ModelMetrics } from '../types'
import { CardSkeleton } from '../components/ui/LoadingSkeleton'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { EmptyState }   from '../components/ui/EmptyState'
import { Brain }        from 'lucide-react'
import { formatDateTime, formatPct } from '../utils/format'
import { useToast }     from '../store/toast'
import { DecisionBadge } from '../components/ui/Badge'

const FI_COLORS = ['#06b6d4','#a78bfa','#34d399','#f59e0b','#f472b6','#ef4444']

function MetricTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-[var(--bg-secondary)] rounded-lg p-3 text-center">
      <p className="text-[10px] text-[var(--text-secondary)] uppercase tracking-wide">{label}</p>
      <p className="text-lg font-bold font-mono text-[var(--text-primary)] mt-1">{value}</p>
    </div>
  )
}

function ConfusionMatrix({ matrix, labels }: { matrix: number[][]; labels: string[] }) {
  const total = matrix.flat().reduce((a,b)=>a+b,0)
  return (
    <div className="overflow-x-auto">
      <table className="text-xs border-collapse">
        <thead>
          <tr>
            <th className="px-2 py-1 text-[var(--text-secondary)]">Actual ↓ / Predicted →</th>
            {labels.map(l => <th key={l} className="px-3 py-1 text-center font-semibold text-[var(--text-secondary)]">{l}</th>)}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, i) => (
            <tr key={i}>
              <td className="px-2 py-1 font-semibold text-[var(--text-secondary)]">{labels[i]}</td>
              {row.map((val, j) => {
                const pct = total > 0 ? val/total : 0
                const onDiag = i === j
                return (
                  <td key={j} className="px-3 py-2 text-center rounded"
                    style={{ background: onDiag ? `rgba(6,182,212,${0.1+pct*2})` : `rgba(239,68,68,${pct*2})` }}>
                    <span className={`font-mono font-bold ${onDiag ? 'text-cyan-300' : val > 0 ? 'text-red-300' : 'text-[var(--text-secondary)]'}`}>
                      {val}
                    </span>
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

const DEFAULT_FEATURES = { temperature: 55, pressure: 4.5, vibration: 1.5, rpm: 1800, current: 7.0, torque: 40 }

export default function Analytics() {
  const { show }         = useToast()
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState<string | null>(null)
  const [features, setFeatures] = useState<Record<string, number>>(DEFAULT_FEATURES)
  const [predResult, setPredResult] = useState<Record<string, unknown> | null>(null)
  const [predLoading, setPredLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    fetchAnalyticsMetrics()
      .then(r => setMetrics((r as { data: ModelMetrics }).data))
      .catch(e => setError((e as Error).message))
      .finally(() => setLoading(false))
  }, [])

  const handlePredict = async () => {
    setPredLoading(true)
    try {
      const res = await postDecisionEvaluate({ ...features, machine_id: 'MANUAL' }) as { data: Record<string, unknown> }
      setPredResult(res.data)
      show('Prediction complete', 'success')
    } catch (e: unknown) {
      show((e as Error).message, 'error')
    } finally { setPredLoading(false) }
  }

  if (loading) return <div className="space-y-4">{Array.from({length:4}).map((_,i)=><CardSkeleton key={i}/>)}</div>
  if (error)   return <ErrorMessage message={error}/>
  if (!metrics?.model_available) return (
    <EmptyState icon={Brain} title="Model not trained"
      message="Train the model from the Data Lab to view analytics."
      action={<a href="/data-lab" className="btn-primary text-sm">Go to Data Lab</a>}/>
  )

  const fiData = Object.entries(metrics.feature_importance ?? {})
    .sort((a,b) => b[1]-a[1])
    .map(([name, value]) => ({ name, value: +(value*100).toFixed(1) }))

  return (
    <div className="space-y-5">
      <div>
        <h2 className="page-title">Predictive Analytics</h2>
        <p className="page-subtitle">
          Random Forest classifier — trained at {metrics.trained_at ? formatDateTime(metrics.trained_at) : '—'}
        </p>
        {metrics.disclosure && (
          <p className="text-xs text-amber-400 mt-1 italic">{metrics.disclosure}</p>
        )}
      </div>

      {/* Overview metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <MetricTile label="Accuracy"        value={formatPct(metrics.accuracy ?? 0)}/>
        <MetricTile label="Macro F1"        value={formatPct(metrics.macro_f1 ?? 0)}/>
        <MetricTile label="Macro Precision" value={formatPct(metrics.macro_precision ?? 0)}/>
        <MetricTile label="Macro Recall"    value={formatPct(metrics.macro_recall ?? 0)}/>
        <MetricTile label="Dataset Size"    value={(metrics.dataset_size ?? 0).toLocaleString()}/>
        <MetricTile label="Train Samples"   value={(metrics.train_size ?? 0).toLocaleString()}/>
        <MetricTile label="Test Samples"    value={(metrics.test_size ?? 0).toLocaleString()}/>
        <MetricTile label="Weighted F1"     value={formatPct(metrics.weighted_f1 ?? 0)}/>
      </div>

      {/* Per-class + Confusion matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card">
          <p className="section-title">Per-class Metrics</p>
          <div className="table-container">
            <table className="table">
              <thead><tr><th>Class</th><th>Precision</th><th>Recall</th><th>F1</th><th>Support</th></tr></thead>
              <tbody>
                {Object.entries(metrics.per_class ?? {}).map(([cls, m]) => (
                  <tr key={cls}>
                    <td className="font-semibold">{cls}</td>
                    <td className="font-mono text-xs">{formatPct(m.precision)}</td>
                    <td className="font-mono text-xs">{formatPct(m.recall)}</td>
                    <td className="font-mono text-xs">{formatPct(m.f1)}</td>
                    <td className="font-mono text-xs">{m.support}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card">
          <p className="section-title">Confusion Matrix</p>
          {metrics.confusion_matrix && metrics.labels ? (
            <ConfusionMatrix matrix={metrics.confusion_matrix} labels={metrics.labels}/>
          ) : <p className="text-sm text-[var(--text-secondary)]">Not available</p>}
        </div>
      </div>

      {/* Feature importance */}
      <div className="card">
        <p className="section-title">Feature Importance</p>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={fiData} layout="vertical" margin={{ left: 60, right: 20 }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={false}/>
            <XAxis type="number" tick={{ fontSize: 10 }} tickFormatter={v => `${v}%`}/>
            <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={60}/>
            <Tooltip contentStyle={{ background:'#0d1526', border:'1px solid #1e2d4a', borderRadius:6, fontSize:11 }}
              formatter={(v: unknown) => [`${v}%`,'Importance']}/>
            <Bar dataKey="value" radius={[0,3,3,0]}>
              {fiData.map((_, i) => <Cell key={i} fill={FI_COLORS[i % FI_COLORS.length]}/>)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Manual prediction panel */}
      <div className="card">
        <p className="section-title">Manual Prediction</p>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
          {Object.entries(features).map(([k, v]) => (
            <div key={k}>
              <label className="text-xs text-[var(--text-secondary)] capitalize">{k}</label>
              <input type="number" className="input mt-1 h-8 text-xs"
                value={v}
                onChange={e => setFeatures(f => ({ ...f, [k]: Number(e.target.value) }))}/>
            </div>
          ))}
        </div>
        <button className="btn-primary text-sm" onClick={handlePredict} disabled={predLoading}>
          {predLoading ? 'Running...' : 'Evaluate Decision'}
        </button>
        {predResult && (
          <div className="mt-4 p-3 bg-[var(--bg-secondary)] rounded-lg">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-sm font-semibold">Decision:</span>
              <DecisionBadge decision={predResult.decision as string}/>
            </div>
            <p className="text-xs text-[var(--text-secondary)]">{predResult.reason as string}</p>
          </div>
        )}
      </div>
    </div>
  )
}
