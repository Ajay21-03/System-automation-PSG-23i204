import { Database, type LucideIcon } from 'lucide-react'

interface Props {
  icon?:    LucideIcon
  title:    string
  message?: string
  action?:  React.ReactNode
}

export function EmptyState({ icon: Icon = Database, title, message, action }: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="w-16 h-16 rounded-full bg-[var(--bg-secondary)] flex items-center justify-center mb-4">
        <Icon className="w-8 h-8 text-[var(--text-secondary)]" />
      </div>
      <h3 className="text-base font-semibold text-[var(--text-primary)] mb-1">{title}</h3>
      {message && <p className="text-sm text-[var(--text-secondary)] max-w-sm">{message}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}
