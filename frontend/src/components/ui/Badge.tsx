import clsx from 'clsx'
import type { DecisionKey } from '../../utils/severity'
import { DECISION_COLORS } from '../../utils/severity'

interface Props {
  label:     string
  className?: string
}
export function Badge({ label, className }: Props) {
  return <span className={clsx('badge', className)}>{label}</span>
}

export function DecisionBadge({ decision }: { decision: string }) {
  const key = decision as DecisionKey
  const cls  = DECISION_COLORS[key] ?? 'badge-info'
  const labels: Record<string, string> = {
    SAFE:                 'Safe',
    MONITOR:              'Monitor',
    SCHEDULE_MAINTENANCE: 'Maintenance',
    EMERGENCY_STOP:       'Emergency Stop',
    SAFE_OK:              'Safe',
    WARNING:              'Warning',
  }
  return <span className={clsx('badge', cls)}>{labels[decision] ?? decision}</span>
}

export function SeverityBadge({ severity }: { severity: string }) {
  const cls: Record<string, string> = {
    critical: 'badge-critical',
    warning:  'badge-warning',
    info:     'badge-info',
    ok:       'badge-safe',
  }
  return <span className={clsx('badge', cls[severity] ?? 'badge-info')}>{severity}</span>
}

export function IntegrityBadge({ status }: { status: string }) {
  const cls: Record<string, string> = {
    ok:          'badge-safe',
    suspicious:  'badge-warning',
    compromised: 'badge-critical',
  }
  return <span className={clsx('badge', cls[status] ?? 'badge-info')}>{status}</span>
}
