import React from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { LoginPage } from './pages/LoginPage'
import { StudentDashboard } from './pages/StudentDashboard'
import { PerformancePage } from './pages/PerformancePage'
import { CareerGuidancePage } from './pages/CareerGuidancePage'
import { ChatAdvisorPage } from './pages/ChatAdvisorPage'
import { StudyPlannerPage } from './pages/StudyPlannerPage'
import { WellbeingPage } from './pages/WellbeingPage'
import { MentorDashboard } from './pages/MentorDashboard'
import { AdminDashboard } from './pages/AdminDashboard'
import { SettingsPage } from './pages/SettingsPage'
import { Role } from './types'

function ProtectedRoute({
  children,
  roles,
}: {
  children: React.ReactNode
  roles?: Role[]
}) {
  const { user, loading } = useAuth()
  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#F8FAFC] dark:bg-slate-950">
        <p className="text-base font-semibold text-slate-600 dark:text-slate-300">
          Loading AdvisorAI...
        </p>
      </div>
    )
  }
  if (!user) return <Navigate to="/login" replace />
  if (roles && !roles.includes(user.role)) {
    if (user.role === 'mentor') return <Navigate to="/mentor" replace />
    if (user.role === 'admin') return <Navigate to="/admin" replace />
    return <Navigate to="/" replace />
  }
  return <>{children}</>
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute roles={['student']}>
                <StudentDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/performance"
            element={
              <ProtectedRoute roles={['student']}>
                <PerformancePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/careers"
            element={
              <ProtectedRoute roles={['student']}>
                <CareerGuidancePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/chat"
            element={
              <ProtectedRoute roles={['student']}>
                <ChatAdvisorPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/planner"
            element={
              <ProtectedRoute roles={['student']}>
                <StudyPlannerPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/wellbeing"
            element={
              <ProtectedRoute roles={['student']}>
                <WellbeingPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/mentor"
            element={
              <ProtectedRoute roles={['mentor', 'admin']}>
                <MentorDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <ProtectedRoute roles={['admin']}>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <SettingsPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
