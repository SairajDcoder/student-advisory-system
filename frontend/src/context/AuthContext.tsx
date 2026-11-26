import React, { createContext, useContext, useEffect, useState } from 'react'
import { apiRequest } from '../lib/api'
import { supabase } from '../lib/supabase'
import { User } from '../types'

interface AuthContextValue {
  user: User | null
  loading: boolean
  theme: 'light' | 'dark'
  toggleTheme: () => void
  setThemeMode: (mode: 'light' | 'dark') => void
  refreshUser: () => Promise<User | null>
  logout: () => Promise<void>
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

  const refreshUser = async (): Promise<User | null> => {
    const {
      data: { session },
    } = await supabase.auth.getSession()

    if (!session?.access_token) {
      setUser(null)
      setLoading(false)
      return null
    }
    try {
      const me = await apiRequest<User>('/api/auth/me')
      setUser(me)
      if (me.theme_preference === 'dark' || me.theme_preference === 'light') {
        setTheme(me.theme_preference)
      }
      return me
    } catch {
      setUser(null)
      return null
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refreshUser()
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session?.access_token) {
        refreshUser()
      } else {
        setUser(null)
        setLoading(false)
      }
    })
    return () => subscription.unsubscribe()
  }, [])

  const logout = async () => {
    await supabase.auth.signOut()
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
