import clsx from 'clsx'
import type { LucideIcon } from 'lucide-react'

interface Props {
  label:     string
  value:     string | number
  icon:      LucideIcon
  color?:    'cyan' | 'emerald' | 'amber' | 'red' | 'blue' | 'purple'
  subtitle?: string
  onClick?:  () => void
}

const colorMap = {
  cyan:    { icon: 'text-cyan-400',    bg: 'bg-cyan-900/30',    ring: 'ring-cyan-500/20'    },
  emerald: { icon: 'text-emerald-400', bg: 'bg-emerald-900/30', ring: 'ring-emerald-500/20' },
  amber:   { icon: 'text-amber-400',   bg: 'bg-amber-900/30',   ring: 'ring-amber-500/20'   },
  red:     { icon: 'text-red-400',     bg: 'bg-red-900/30',     ring: 'ring-red-500/20'     },
  blue:    { icon: 'text-blue-400',    bg: 'bg-blue-900/30',    ring: 'ring-blue-500/20'    },
  purple:  { icon: 'text-purple-400',  bg: 'bg-purple-900/30',  ring: 'ring-purple-500/20'  },
}

export function KpiCard({ label, value, icon: Icon, color = 'cyan', subtitle, onClick }: Props) {
  const c = colorMap[color]
  return (
    <div
      className={clsx(
        'card flex items-start gap-4 transition-colors',
        onClick && 'cursor-pointer hover:border-[var(--accent)]'
      )}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <div className={clsx('w-10 h-10 rounded-lg flex items-center justify-center ring-1', c.bg, c.ring)}>
        <Icon className={clsx('w-5 h-5', c.icon)} />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-xs font-medium text-[var(--text-secondary)] truncate">{label}</p>
        <p className="text-2xl font-bold text-[var(--text-primary)] mt-0.5 leading-none">{value}</p>
        {subtitle && <p className="text-xs text-[var(--text-secondary)] mt-1">{subtitle}</p>}
      </div>
    </div>
  )
}
