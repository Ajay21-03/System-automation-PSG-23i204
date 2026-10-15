// ── Shared domain types ──────────────────────────────────────────────────────

export type WearLabel      = 'Normal' | 'Warning' | 'Failure'
export type Decision       = 'SAFE' | 'MONITOR' | 'SCHEDULE_MAINTENANCE' | 'EMERGENCY_STOP'
export type IntegrityStatus= 'ok' | 'suspicious' | 'compromised'
export type Severity       = 'info' | 'warning' | 'critical'
export type MaintStatus    = 'open' | 'acknowledged' | 'scheduled' | 'resolved'

export interface ApiResponse<T = unknown> {
  success:   boolean
  message:   string
  timestamp: string
  data?:     T
}

export interface KPIs {
  total_machines:          number
  monitored_records:       number
  normal_machines:         number
  warning_machines:        number
  emergency_stops:         number
  predicted_maintenance:   number
  sensor_integrity_alerts: number
  maintenance_cases_open:  number
  class_distribution:      Record<WearLabel, number>
  machine_statuses:        Record<string, string>
  emergency_arms:          string[]
}

export interface DashboardSummary {
  dataset_available: boolean
  model_available:   boolean
  kpis:              KPIs
  dataset_rows:      number
}

export interface TrendEntry {
  date:    string
  Normal:  number
  Warning: number
  Failure: number
}

export interface DashboardTrends {
  available:     boolean
  trend_series:  TrendEntry[]
  sensor_avgs:   Record<string, number>[]
  recent_events: RecentEvent[]
}

export interface RecentEvent {
  timestamp:   string
  arm_id:      string
  joint:       string
  wear_label:  WearLabel
  temperature: number
  vibration:   number
  torque:      number
}

export interface Machine {
  arm_id:           string
  status:           string
  last_timestamp:   string
  wear_label:       WearLabel
  temperature:      number
  vibration:        number
  torque:           number
  rpm:              number
  current:          number
  pressure:         number
  sensor_integrity: IntegrityStatus
  joint:            string
  record_count:     number
}

export interface JointInfo {
  temperature: number
  vibration:   number
  torque:      number
  rpm:         number
  current:     number
  wear_label:  WearLabel
  record_count:number
}

export interface MachineDetail {
  arm_id:          string
  latest_reading:  Record<string, unknown>
  decision:        Decision
  reason:          string
  evidence:        string[]
  joints:          Record<string, JointInfo>
  history:         SensorReading[]
  recent_events:   RecentEvent[]
  rule_result:     RuleResult
  ml_result:       MLResult | null
}

export interface SensorReading {
  timestamp:   string
  arm_id:      string
  joint:       string
  temperature: number
  pressure:    number
  vibration:   number
  rpm:         number
  current:     number
  torque:      number
  wear_label:  WearLabel
  sensor_integrity: IntegrityStatus
  threshold_flags?: Record<string, string>
}

export interface RuleResult {
  triggered_rules: TriggeredRule[]
  has_critical:    boolean
  has_warning:     boolean
  rule_action:     string | null
  evidence:        string[]
}

export interface TriggeredRule {
  rule_id:   string
  name:      string
  sensor:    string
  severity:  Severity
  action:    string
  threshold: number
  value:     number
}

export interface MLResult {
  predicted_class: WearLabel
  probabilities:   Record<WearLabel, number>
  features_used:   Record<string, number>
  predicted_at:    string
  model_available: boolean
  error?:          string
}

export interface ModelMetrics {
  model_available:   boolean
  trained_at?:       string
  dataset_size?:     number
  train_size?:       number
  test_size?:        number
  accuracy?:         number
  macro_precision?:  number
  macro_recall?:     number
  macro_f1?:         number
  weighted_precision?:number
  weighted_recall?:  number
  weighted_f1?:      number
  per_class?:        Record<string, ClassMetrics>
  confusion_matrix?: number[][]
  labels?:           string[]
  feature_importance?:Record<string, number>
  class_distribution?:Record<string, number>
  disclosure?:       string
}

export interface ClassMetrics {
  precision: number
  recall:    number
  f1:        number
  support:   number
}

export interface MaintenanceCase {
  id:          number
  machine_id:  string
  joint:       string | null
  decision:    string
  severity:    Severity
  status:      MaintStatus
  description: string
  evidence:    string
  priority:    string
  created_at:  string
  updated_at:  string
}

export interface MaintenanceLogEntry {
  id:             number
  machine_id:     string | null
  joint:          string | null
  text:           string
  severity:       Severity
  relevant:       number
  detected_terms: string
  explanation:    string
  analyzed_at:    string
  created_at:     string
}

export interface SecurityEvent {
  id:          number
  machine_id:  string
  sensor:      string
  severity:    Severity
  reason:      string
  value:       string
  detected_at: string
}

export interface Rule {
  id:             string
  name:           string
  description:    string
  sensor:         string
  threshold:      number
  operator:       string
  severity:       Severity
  action:         string
  enabled:        boolean
  safety_critical:boolean
  trigger_count:  number
  last_triggered: string | null
}

export interface AuditEvent {
  timestamp:   string
  event_type:  string
  machine_id:  string | null
  severity:    string
  source:      string
  description: string
  decision:    string | null
  evidence:    Record<string, unknown>
}

export interface DatasetSummary {
  available:          boolean
  rows?:              number
  columns?:           string[]
  column_stats?:      Record<string, ColumnStats>
  class_distribution?:Record<string, number>
  validation?:        ValidationResult
  path?:              string
  disclosure?:        string
}

export interface ColumnStats {
  min:   number
  max:   number
  mean:  number
  std:   number
  nulls: number
}

export interface ValidationResult {
  passed:   boolean
  checks:   ValidationCheck[]
  rows:     number
  summary:  string
}

export interface ValidationCheck {
  check:  string
  passed: boolean
  detail: string
}

export interface SystemStatus {
  version:        string
  dataset_exists: boolean
  model_exists:   boolean
  db_exists:      boolean
  model_loaded:   boolean
  dataset_path:   string
  model_path:     string
  thresholds:     Record<string, number>
}
