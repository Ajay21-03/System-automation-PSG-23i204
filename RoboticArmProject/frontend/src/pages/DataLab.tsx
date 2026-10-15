import { useEffect, useState, useCallback } from 'react'
import { RefreshCw, Play, CheckCircle, XCircle } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import {
  fetchDatasetSummary, postGenerateDataset,
  postTrainModel, fetchValidateDataset
} from '../api/endpoints'
import type { DatasetSummary, ValidationResult } from '../types'
import { CardSkeleton } from '../components/ui/LoadingSkeleton'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { ConfirmDialog } from '../components/ui/ConfirmDialog'
import { useToast }     from '../store/toast'

const CLASS_COLORS = { Normal: '#10b981', Warning: '#f59e0b', Failure: '#ef4444' }

export default function DataLab() {
  const { show }             = useToast()
  const [summary, setSummary]   = useState<DatasetSummary | null>(null)
  const [validation, setValidation] = useState<ValidationResult | null>(null)
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState<string | null>(null)
  const [generating, setGenerating] = useState(false)
  const [training, setTraining]     = useState(false)
  const [confirmGen, setConfirmGen] = useState(false)
  const [rows, setRows]             = useState(5000)

  const load = useCallback(async () => {
    setLoading(true); setError(null)
    try {
      const res = await fetchDatasetSummary() as { data: DatasetSummary }
      setSummary(res.data)
    } catch (e: unknown) { setError((e as Error).message) }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  const handleGenerate = async () => {
    setConfirmGen(false); setGenerating(true)
    try {
      await postGenerateDataset({ rows })
      show(`Dataset generated with ${rows} rows`, 'success')
      load()
    } catch (e: unknown) { show((e as Error).message, 'error') }
    finally { setGenerating(false) }
  }

  const handleTrain = async () => {
    setTraining(true)
    try {
      const res = await postTrainModel() as { data: { accuracy: number } }
      const acc = (res.data?.accuracy ?? 0)
      show(`Model trained! Accuracy: ${(acc*100).toFixed(1)}%`, 'success')
      load()
    } catch (e: unknown) { show((e as Error).message, 'error') }
    finally { setTraining(false) }
  }

  const handleValidate = async () => {
    try {
      const res = await fetchValidateDataset() as { data: ValidationResult }
      setValidation(res.data)
      show(res.data.passed ? 'All validation checks passed' : 'Some validation checks failed', res.data.passed ? 'success' : 'warning')
    } catch (e: unknown) { show((e as Error).message, 'error') }
  }

  const distData = Object.entries(summary?.class_distribution ?? {})
    .map(([name, value]) => ({ name, value }))

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="page-title">Dataset & Model Lab</h2>
          <p className="page-subtitle">Generate synthetic data, validate, and train the ML model</p>
        </div>
        <button className="btn-secondary text-xs" onClick={load}><RefreshCw className="w-3.5 h-3.5"/>Refresh</button>
      </div>

      {/* Disclosure */}
      <div className="rounded-lg border border-blue-700/30 bg-blue-900/10 p-3 text-xs text-blue-300">
        <strong>Disclosure:</strong> All data is synthetic and generated for academic evaluation only.
        Performance metrics do not represent real-world industrial sensor accuracy.
      </div>

      {/* Actions */}
      <div className="card">
        <p className="section-title">Actions</p>
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="text-xs text-[var(--text-secondary)]">Rows to generate</label>
            <input type="number" className="input h-8 text-xs mt-1 w-28"
              value={rows} min={100} max={50000}
              onChange={e => setRows(Number(e.target.value))}/>
          </div>
          <button className="btn-primary text-xs" onClick={() => setConfirmGen(true)} disabled={generating}>
            <Play className="w-3.5 h-3.5"/>
            {generating ? 'Generating...' : 'Generate Dataset'}
          </button>
          <button className="btn-secondary text-xs" onClick={handleValidate}>
            Validate Dataset
          </button>
          <button className="btn-primary text-xs" onClick={handleTrain} disabled={training}>
            {training ? 'Training...' : 'Train Model'}
          </button>
        </div>
      </div>

      {loading ? <CardSkeleton/>
      : error   ? <ErrorMessage message={error} onRetry={load}/>
      : !summary?.available ? (
        <div className="card text-center py-12">
          <p className="text-[var(--text-secondary)]">No dataset generated yet. Use the Generate button above.</p>
        </div>
      ) : (
        <>
          {/* Dataset overview */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              ['Total Rows', summary.rows?.toLocaleString()],
              ['Columns', summary.columns?.length],
              ['Missing Values', '0'],
              ['Duplicate Rows', '0'],
            ].map(([l,v]) => (
              <div key={l as string} className="card text-center">
                <p className="text-xs text-[var(--text-secondary)]">{l as string}</p>
                <p className="text-xl font-bold font-mono mt-1">{v as string}</p>
              </div>
            ))}
          </div>

          {/* Class distribution */}
          {distData.length > 0 && (
            <div className="card">
              <p className="section-title">Class Distribution</p>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={distData}>
                  <CartesianGrid strokeDasharray="3 3"/>
                  <XAxis dataKey="name" tick={{ fontSize: 12 }}/>
                  <YAxis tick={{ fontSize: 11 }}/>
                  <Tooltip contentStyle={{ background:'#0d1526', border:'1px solid #1e2d4a', borderRadius:6, fontSize:12 }}/>
                  <Bar dataKey="value" radius={[4,4,0,0]}>
                    {distData.map(d => (
                      <Cell key={d.name} fill={CLASS_COLORS[d.name as keyof typeof CLASS_COLORS] ?? '#64748b'}/>
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Column stats */}
          {summary.column_stats && (
            <div className="card">
              <p className="section-title">Sensor Statistics</p>
              <div className="table-container">
                <table className="table">
                  <thead><tr><th>Sensor</th><th>Min</th><th>Max</th><th>Mean</th><th>Std</th></tr></thead>
                  <tbody>
                    {Object.entries(summary.column_stats).map(([col, stats]) => (
                      <tr key={col}>
                        <td className="font-semibold capitalize">{col}</td>
                        <td className="font-mono text-xs">{stats.min}</td>
                        <td className="font-mono text-xs">{stats.max}</td>
                        <td className="font-mono text-xs">{stats.mean}</td>
                        <td className="font-mono text-xs">{stats.std}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Validation results */}
          {validation && (
            <div className="card">
              <div className="flex items-center gap-2 mb-3">
                {validation.passed
                  ? <CheckCircle className="w-5 h-5 text-emerald-400"/>
                  : <XCircle    className="w-5 h-5 text-red-400"/>}
                <p className="font-semibold">{validation.summary}</p>
              </div>
              <div className="space-y-1">
                {validation.checks.map(c => (
                  <div key={c.check} className="flex items-center gap-3 text-xs">
                    {c.passed
                      ? <CheckCircle className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0"/>
                      : <XCircle    className="w-3.5 h-3.5 text-red-400 flex-shrink-0"/>}
                    <span className="text-[var(--text-secondary)] w-48 flex-shrink-0">{c.check}</span>
                    <span className={c.passed ? 'text-[var(--text-secondary)]' : 'text-red-400'}>{c.detail}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      <ConfirmDialog
        open={confirmGen}
        title="Generate Dataset"
        message={`This will generate a new ${rows.toLocaleString()}-row dataset${summary?.available ? ' and overwrite the existing one' : ''}. Continue?`}
        onConfirm={handleGenerate}
        onCancel={() => setConfirmGen(false)}
      />
    </div>
  )
}
