import React, { createContext, useContext, useEffect, useState } from 'react'
import { apiRequest } from '../lib/api'
import { User } from '../types'

interface AuthContextValue {
  user: User | null
  loading: boolean
  theme: 'light' | 'dark'
  toggleTheme: () => void
  setThemeMode: (mode: 'light' | 'dark') => void
  loginSuccess: (token: string, user: User) => void
  refreshUser: () => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const saved = localStorage.getItem('advisorai_theme')
    return saved === 'dark' ? 'dark' : 'light'
  })

  useEffect(() => {
    const root = document.documentElement
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    localStorage.setItem('advisorai_theme', theme)
  }, [theme])

  const refreshUser = async () => {
    const token = localStorage.getItem('advisorai_token')
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }
    try {
      const me = await apiRequest<User>('/api/auth/me')
      setUser(me)
      if (me.theme_preference === 'dark' || me.theme_preference === 'light') {
        setTheme(me.theme_preference)
      }
    } catch {
      localStorage.removeItem('advisorai_token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refreshUser()
  }, [])

  const loginSuccess = (token: string, u: User) => {
    localStorage.setItem('advisorai_token', token)
    setUser(u)
  }

  const logout = () => {
    localStorage.removeItem('advisorai_token')
    setUser(null)
  }

  const toggleTheme = () => setTheme((prev) => (prev === 'light' ? 'dark' : 'light'))
  const setThemeMode = (mode: 'light' | 'dark') => setTheme(mode)

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        theme,
        toggleTheme,
        setThemeMode,
        loginSuccess,
        refreshUser,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
