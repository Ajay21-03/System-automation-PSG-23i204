import { Sun, Moon, Bell, Menu, Wifi, WifiOff } from 'lucide-react'
import { useTheme } from '../../store/theme'
import { format } from 'date-fns'
import { useEffect, useState } from 'react'
import { fetchHealth } from '../../api/endpoints'

interface Props { title: string; onMenuClick: () => void }

export function TopBar({ title, onMenuClick }: Props) {
  const { theme, toggle } = useTheme()
  const [now, setNow]       = useState(new Date())
  const [online, setOnline] = useState<boolean | null>(null)

  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(t)
  }, [])

  useEffect(() => {
    let mounted = true
    const check = async () => {
      try {
        await fetchHealth()
        if (mounted) setOnline(true)
      } catch {
        if (mounted) setOnline(false)
      }
    }
    check()
    const t = setInterval(check, 15000)
    return () => { mounted = false; clearInterval(t) }
  }, [])

  return (
    <header className="flex items-center justify-between px-4 py-3 border-b border-[var(--border)] bg-[var(--bg-secondary)]">
      <div className="flex items-center gap-3">
        <button onClick={onMenuClick} className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] lg:hidden">
          <Menu className="w-5 h-5" />
        </button>
        <h1 className="text-sm font-semibold text-[var(--text-primary)] truncate">{title}</h1>
      </div>

      <div className="flex items-center gap-3">
        {/* API status */}
        <div className="flex items-center gap-1.5 text-xs text-[var(--text-secondary)]">
          {online === null ? null : online ? (
            <><Wifi className="w-3.5 h-3.5 text-emerald-400" /><span className="hidden sm:inline text-emerald-400">API Online</span></>
          ) : (
            <><WifiOff className="w-3.5 h-3.5 text-red-400" /><span className="hidden sm:inline text-red-400">API Offline</span></>
          )}
        </div>

        {/* Clock */}
        <span className="text-xs text-[var(--text-secondary)] font-mono hidden sm:block">
          {format(now, 'HH:mm:ss')}
        </span>

        {/* Theme */}
        <button
          onClick={toggle}
          className="w-8 h-8 rounded-md flex items-center justify-center text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-panel)] transition-colors"
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>

        {/* Notifications placeholder */}
        <button className="w-8 h-8 rounded-md flex items-center justify-center text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-panel)] transition-colors relative">
          <Bell className="w-4 h-4" />
        </button>
      </div>
    </header>
  )
}
