import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Cpu, Activity, BarChart2, Wrench, FileText,
  Shield, Zap, ScrollText, Database, Settings, ChevronLeft, ChevronRight,
  Gauge
} from 'lucide-react'
import clsx from 'clsx'

interface Props { collapsed: boolean; toggle: () => void }

const NAV = [
  { to: '/dashboard',       label: 'Dashboard',       icon: LayoutDashboard },
  { to: '/fleet',           label: 'Machine Fleet',   icon: Cpu             },
  { to: '/monitoring',      label: 'Sensor Monitor',  icon: Activity        },
  { to: '/analytics',       label: 'ML Analytics',    icon: BarChart2       },
  { to: '/maintenance',     label: 'Maintenance',     icon: Wrench          },
  { to: '/maintenance-logs',label: 'Maint. Logs',     icon: FileText        },
  { to: '/security',        label: 'Security',        icon: Shield          },
  { to: '/automation',      label: 'Rule Engine',     icon: Zap             },
  { to: '/logs',            label: 'Audit Logs',      icon: ScrollText      },
  { to: '/data-lab',        label: 'Data Lab',        icon: Database        },
  { to: '/settings',        label: 'Settings',        icon: Settings        },
]

export function Sidebar({ collapsed, toggle }: Props) {
  const loc = useLocation()

  return (
    <aside className={clsx(
      'flex flex-col border-r border-[var(--border)] bg-[var(--bg-secondary)] transition-all duration-200',
      collapsed ? 'w-16' : 'w-60'
    )}>
      {/* Brand */}
      <div className={clsx(
        'flex items-center gap-3 px-4 py-5 border-b border-[var(--border)]',
        collapsed && 'justify-center px-2'
      )}>
        <div className="w-8 h-8 rounded-lg bg-cyan-600/20 flex items-center justify-center ring-1 ring-cyan-500/30 flex-shrink-0">
          <Gauge className="w-4 h-4 text-cyan-400" />
        </div>
        {!collapsed && (
          <div className="overflow-hidden">
            <div className="text-xs font-bold text-white leading-tight whitespace-nowrap truncate">
              IICC
            </div>
            <div className="text-[10px] text-[var(--text-secondary)] truncate">
              23IF02 System Automation
            </div>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-3 space-y-0.5 px-2">
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to} to={to}
            className={({ isActive }) => clsx(
              'flex items-center gap-3 px-2 py-2 rounded-md text-sm font-medium transition-colors group',
              collapsed ? 'justify-center' : '',
              isActive
                ? 'bg-cyan-900/40 text-cyan-300 border border-cyan-700/30'
                : 'text-[var(--text-secondary)] hover:bg-[var(--bg-panel)] hover:text-[var(--text-primary)]'
            )}
            title={collapsed ? label : undefined}
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            {!collapsed && <span className="truncate">{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={toggle}
        className="flex items-center justify-center p-3 border-t border-[var(--border)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-panel)] transition-colors"
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? <ChevronRight className="w-4 h-4" /> : (
          <span className="flex items-center gap-2 text-xs">
            <ChevronLeft className="w-4 h-4" />
            {!collapsed && 'Collapse'}
          </span>
        )}
      </button>
    </aside>
  )
}
