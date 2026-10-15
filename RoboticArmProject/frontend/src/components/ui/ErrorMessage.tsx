import { AlertTriangle, RefreshCw } from 'lucide-react'

interface Props {
  message: string
  onRetry?: () => void
}
export function ErrorMessage({ message, onRetry }: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-3">
      <div className="w-12 h-12 rounded-full bg-red-900/30 flex items-center justify-center">
        <AlertTriangle className="w-6 h-6 text-red-400" />
      </div>
      <p className="text-sm text-red-400 text-center max-w-sm">{message}</p>
      {onRetry && (
        <button className="btn-secondary" onClick={onRetry}>
          <RefreshCw className="w-4 h-4" />
          Retry
        </button>
      )}
    </div>
  )
}
