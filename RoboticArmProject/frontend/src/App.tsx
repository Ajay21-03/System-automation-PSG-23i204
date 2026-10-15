import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from './store/theme'
import { ToastProvider } from './store/toast'
import { AppShell }      from './components/layout/AppShell'

import Dashboard        from './pages/Dashboard'
import Fleet            from './pages/Fleet'
import MachineDetail    from './pages/MachineDetail'
import Monitoring       from './pages/Monitoring'
import Analytics        from './pages/Analytics'
import MaintenancePage  from './pages/Maintenance'
import MaintenanceLogs  from './pages/MaintenanceLogs'
import Security         from './pages/Security'
import Automation       from './pages/Automation'
import Logs             from './pages/Logs'
import DataLab          from './pages/DataLab'
import Settings         from './pages/Settings'

export default function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<AppShell />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard"        element={<Dashboard />} />
              <Route path="fleet"            element={<Fleet />} />
              <Route path="fleet/:armId"     element={<MachineDetail />} />
              <Route path="monitoring"       element={<Monitoring />} />
              <Route path="analytics"        element={<Analytics />} />
              <Route path="maintenance"      element={<MaintenancePage />} />
              <Route path="maintenance-logs" element={<MaintenanceLogs />} />
              <Route path="security"         element={<Security />} />
              <Route path="automation"       element={<Automation />} />
              <Route path="logs"             element={<Logs />} />
              <Route path="data-lab"         element={<DataLab />} />
              <Route path="settings"         element={<Settings />} />
              <Route path="*"                element={<Navigate to="/dashboard" replace />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </ThemeProvider>
  )
}
