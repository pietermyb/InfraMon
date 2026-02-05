import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from './hooks/useTheme'
import { ToastProvider } from './context/ToastContext'
import { AuthProvider } from './hooks/useAuth'
import Layout from './components/layout/Layout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import ContainersPage from './pages/ContainersPage'
import ContainerDetailPage from './pages/ContainerDetailPage'
import SettingsPage from './pages/SettingsPage'
import ProtectedRoute from './components/auth/ProtectedRoute'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <ToastProvider>
            <BrowserRouter>
              <AuthProvider>
                <Routes>
              <Route path="/login" element={<LoginPage />} />
              
              <Route path="/" element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="containers" element={<ContainersPage />} />
                <Route path="containers/:id" element={<ContainerDetailPage />} />
                <Route path="settings" element={<SettingsPage />} />
              </Route>
              
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </AuthProvider>
            </BrowserRouter>
        </ToastProvider>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App
