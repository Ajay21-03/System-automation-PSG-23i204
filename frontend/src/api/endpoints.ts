import { get, post, patch } from './client'
import type { ApiResponse } from '../types'

// Health
export const fetchHealth = () => get<ApiResponse>('/health')

// Dashboard
export const fetchDashboardSummary = () => get<ApiResponse>('/dashboard/summary')
export const fetchDashboardTrends  = () => get<ApiResponse>('/dashboard/trends')

// Fleet
export const fetchFleet = (params?: Record<string, unknown>) =>
  get<ApiResponse>('/fleet', params)
export const fetchMachine = (armId: string) =>
  get<ApiResponse>(`/fleet/${armId}`)

// Monitoring
export const fetchReadings = (params?: Record<string, unknown>) =>
  get<ApiResponse>('/monitoring/readings', params)

// Analytics
export const fetchAnalyticsMetrics = () => get<ApiResponse>('/analytics/metrics')

// Predict
export const postPredict = (payload: Record<string, number>) =>
  post<ApiResponse>('/predict', payload)
export const postDecisionEvaluate = (payload: Record<string, unknown>) =>
  post<ApiResponse>('/decisions/evaluate', payload)
export const fetchDecisionsDemo = () => get<ApiResponse>('/decisions/demo')

// Maintenance
export const fetchMaintenance  = (params?: Record<string, unknown>) =>
  get<ApiResponse>('/maintenance', params)
export const postMaintenance   = (payload: Record<string, unknown>) =>
  post<ApiResponse>('/maintenance', payload)
export const patchMaintenance  = (id: number, payload: Record<string, unknown>) =>
  patch<ApiResponse>(`/maintenance/${id}`, payload)

// Maintenance Logs
export const fetchMaintenanceLogs = (params?: Record<string, unknown>) =>
  get<ApiResponse>('/maintenance-logs', params)
export const postMaintenanceLog   = (payload: { text: string }) =>
  post<ApiResponse>('/maintenance-logs', payload)
export const fetchAnalyzeLogFile  = () =>
  get<ApiResponse>('/maintenance-logs/analyze-file')

// Security
export const fetchSecurityEvents  = (params?: Record<string, unknown>) =>
  get<ApiResponse>('/security/events', params)
export const postSecuritySimulate = (payload: Record<string, unknown>) =>
  post<ApiResponse>('/security/simulate', payload)
export const postSecurityCheck    = (payload: Record<string, unknown>) =>
  post<ApiResponse>('/security/check', payload)
export const fetchSecurityScan    = () => get<ApiResponse>('/security/scan-dataset')

// Automation
export const fetchRules = () => get<ApiResponse>('/automation/rules')

// Logs
export const fetchLogs = (params?: Record<string, unknown>) =>
  get<ApiResponse>('/logs', params)

// Dataset
export const fetchDatasetSummary  = () => get<ApiResponse>('/dataset/summary')
export const postGenerateDataset  = (payload: Record<string, unknown>) =>
  post<ApiResponse>('/dataset/generate', payload)
export const fetchValidateDataset = () => get<ApiResponse>('/dataset/validate')

// Model
export const postTrainModel   = () => post<ApiResponse>('/model/train')
export const fetchModelStatus = () => get<ApiResponse>('/model/status')

// System
export const fetchSystemStatus = () => get<ApiResponse>('/system/status')
