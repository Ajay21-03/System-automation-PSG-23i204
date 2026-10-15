import axios from 'axios'
import type { AxiosError } from 'axios'

// Proxy configured in vite.config.ts: /api → http://localhost:5000
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (res) => res,
  (err: AxiosError) => {
    const msg = (err.response?.data as Record<string, string>)?.message
      ?? err.message
      ?? 'Network error'
    return Promise.reject(new Error(msg))
  }
)

export default api

// ── Typed helpers ────────────────────────────────────────────────────────────
export const get  = <T>(url: string, params?: Record<string, unknown>) =>
  api.get<T>(url, { params }).then(r => r.data)

export const post = <T>(url: string, data?: unknown) =>
  api.post<T>(url, data).then(r => r.data)

export const patch = <T>(url: string, data?: unknown) =>
  api.patch<T>(url, data).then(r => r.data)
