import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { Toaster } from 'react-hot-toast'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import LoanApplication from './pages/LoanApplication'
import ExplanationDashboard from './pages/ExplanationDashboard'
import VoiceAssistant from './pages/VoiceAssistant'
import ConsentDashboard from './pages/ConsentDashboard'
import ProfileExplanation from './pages/ProfileExplanation'
import GovernanceDashboard from './pages/GovernanceDashboard'
import PrivateRoute from './components/PrivateRoute'

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/dashboard"
              element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              }
            />
            {/* User-only routes */}
            <Route
              path="/apply"
              element={
                <PrivateRoute allowedRoles={['user']}>
                  <LoanApplication />
                </PrivateRoute>
              }
            />
            <Route
              path="/explain/:applicationId"
              element={
                <PrivateRoute>
                  <ExplanationDashboard />
                </PrivateRoute>
              }
            />
            <Route
              path="/voice"
              element={
                <PrivateRoute>
                  <VoiceAssistant />
                </PrivateRoute>
              }
            />
            <Route
              path="/consent"
              element={
                <PrivateRoute allowedRoles={['user']}>
                  <ConsentDashboard />
                </PrivateRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <PrivateRoute allowedRoles={['user']}>
                  <ProfileExplanation />
                </PrivateRoute>
              }
            />
            <Route
              path="/governance"
              element={
                <PrivateRoute allowedRoles={['admin', 'auditor']}>
                  <GovernanceDashboard />
                </PrivateRoute>
              }
            />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#fff',
                color: '#0F172A',
                borderRadius: '8px',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
              },
              success: {
                iconTheme: {
                  primary: '#10b981',
                  secondary: '#fff',
                },
              },
              error: {
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
              },
            }}
          />
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App

