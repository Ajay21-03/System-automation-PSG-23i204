import React, { createContext, useCallback, useContext, useState } from 'react'
import { X, CheckCircle, AlertTriangle, XCircle, Info } from 'lucide-react'

export type ToastType = 'success' | 'warning' | 'error' | 'info'
interface Toast { id: number; type: ToastType; message: string }
interface ToastCtx { show: (msg: string, type?: ToastType) => void }

const ToastContext = createContext<ToastCtx>({ show: () => {} })

const ICONS = {
  success: <CheckCircle className="w-4 h-4 text-emerald-400" />,
  warning: <AlertTriangle className="w-4 h-4 text-amber-400" />,
  error:   <XCircle className="w-4 h-4 text-red-400" />,
  info:    <Info className="w-4 h-4 text-cyan-400" />,
}
const BG = {
  success: 'border-emerald-700/50 bg-emerald-900/30',
  warning: 'border-amber-700/50  bg-amber-900/30',
  error:   'border-red-700/50    bg-red-900/30',
  info:    'border-cyan-700/50   bg-cyan-900/30',
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])
  let nextId = 0

  const show = useCallback((message: string, type: ToastType = 'info') => {
    const id = ++nextId
    setToasts(t => [...t, { id, type, message }])
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 4000)
  }, [])

  const dismiss = (id: number) => setToasts(t => t.filter(x => x.id !== id))

  return (
    <ToastContext.Provider value={{ show }}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
        {toasts.map(t => (
          <div key={t.id}
            className={`flex items-start gap-3 p-3 rounded-lg border ${BG[t.type]} backdrop-blur-sm text-sm shadow-xl pointer-events-auto animate-in slide-in-from-right-4`}>
            {ICONS[t.type]}
            <span className="flex-1 text-slate-100">{t.message}</span>
            <button onClick={() => dismiss(t.id)}
              className="text-slate-400 hover:text-white mt-0.5">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export const useToast = () => useContext(ToastContext)
