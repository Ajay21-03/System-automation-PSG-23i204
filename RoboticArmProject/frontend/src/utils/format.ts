import { format, parseISO, formatDistanceToNow } from 'date-fns'

export function formatDate(iso: string): string {
  try { return format(parseISO(iso), 'MMM d, yyyy') } catch { return iso }
}
export function formatDateTime(iso: string): string {
  try { return format(parseISO(iso), 'MMM d, yyyy HH:mm') } catch { return iso }
}
export function formatTimeAgo(iso: string): string {
  try { return formatDistanceToNow(parseISO(iso), { addSuffix: true }) } catch { return iso }
}
export function formatNum(n: number, decimals = 2): string {
  if (n === null || n === undefined) return '—'
  return n.toFixed(decimals)
}
export function formatPct(n: number): string {
  return (n * 100).toFixed(1) + '%'
}
export function clampPct(n: number): number {
  return Math.max(0, Math.min(100, n * 100))
}
