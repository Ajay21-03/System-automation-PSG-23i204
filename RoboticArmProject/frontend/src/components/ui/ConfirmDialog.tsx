import { AlertTriangle } from 'lucide-react'

interface Props {
  open:      boolean
  title:     string
  message:   string
  onConfirm: () => void
  onCancel:  () => void
  danger?:   boolean
}
export function ConfirmDialog({ open, title, message, onConfirm, onCancel, danger }: Props) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="card w-full max-w-md border-[var(--border)] shadow-2xl">
        <div className="flex items-start gap-3 mb-4">
          <AlertTriangle className={`w-5 h-5 mt-0.5 ${danger ? 'text-red-400' : 'text-amber-400'}`} />
          <div>
            <h3 className="font-semibold text-[var(--text-primary)]">{title}</h3>
            <p className="text-sm text-[var(--text-secondary)] mt-1">{message}</p>
          </div>
        </div>
        <div className="flex gap-3 justify-end">
          <button className="btn-secondary" onClick={onCancel}>Cancel</button>
          <button className={danger ? 'btn-danger' : 'btn-primary'} onClick={onConfirm}>Confirm</button>
        </div>
      </div>
    </div>
  )
}
