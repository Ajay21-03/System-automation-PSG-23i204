import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { TopBar }  from './TopBar'

const TITLES: Record<string, string> = {
  '/dashboard':        'Command Center Dashboard',
  '/fleet':            'Machine Fleet',
  '/monitoring':       'Live Sensor Monitoring',
  '/analytics':        'Predictive Analytics',
  '/maintenance':      'Maintenance Intelligence',
  '/maintenance-logs': 'Maintenance Log Intelligence',
  '/security':         'Security & Sensor Integrity',
  '/automation':       'Rule Engine',
  '/logs':             'Event & Audit Logs',
  '/data-lab':         'Dataset & Model Lab',
  '/settings':         'Settings & System Health',
}

export function AppShell() {
  const [collapsed, setCollapsed] = useState(false)
  const loc = useLocation()
  const pathBase = '/' + loc.pathname.split('/')[1]
  const title = TITLES[pathBase] ?? 'Industrial Intelligence Command Center'

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'var(--bg-primary)' }}>
      <Sidebar collapsed={collapsed} toggle={() => setCollapsed(c => !c)} />
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <TopBar title={title} onMenuClick={() => setCollapsed(c => !c)} />
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
