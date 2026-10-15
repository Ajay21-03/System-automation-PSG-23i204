export type DecisionKey = 'SAFE' | 'MONITOR' | 'SCHEDULE_MAINTENANCE' | 'EMERGENCY_STOP'

export const DECISION_LABELS: Record<DecisionKey, string> = {
  SAFE:                 'Safe',
  MONITOR:              'Monitor',
  SCHEDULE_MAINTENANCE: 'Maintenance',
  EMERGENCY_STOP:       'Emergency Stop',
}

export const DECISION_COLORS: Record<DecisionKey, string> = {
  SAFE:                 'badge-safe',
  MONITOR:              'badge-monitor',
  SCHEDULE_MAINTENANCE: 'badge-warning',
  EMERGENCY_STOP:       'badge-critical',
}

export const SEVERITY_COLORS: Record<string, string> = {
  critical:    'text-red-400',
  warning:     'text-amber-400',
  info:        'text-cyan-400',
  ok:          'text-emerald-400',
  suspicious:  'text-amber-400',
  compromised: 'text-red-400',
}

export const DECISION_BG: Record<DecisionKey, string> = {
  SAFE:                 'bg-emerald-900/20 border-emerald-700/30',
  MONITOR:              'bg-cyan-900/20    border-cyan-700/30',
  SCHEDULE_MAINTENANCE: 'bg-amber-900/20   border-amber-700/30',
  EMERGENCY_STOP:       'bg-red-900/30     border-red-600/50',
}
