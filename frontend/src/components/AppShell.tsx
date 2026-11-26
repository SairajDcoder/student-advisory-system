import React, { useEffect, useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  Bell,
  BookOpen,
  CalendarDays,
  Compass,
  GraduationCap,
  HeartHandshake,
  LayoutDashboard,
  LogOut,
  MessageSquareHeart,
  Moon,
  Search,
  Settings,
  ShieldCheck,
  Sun,
  TrendingUp,
  Users,
  X,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { apiRequest } from '../lib/api'
import { NotificationItem } from '../types'

interface NavItem {
  to: string
  label: string
  icon: React.ComponentType<{ className?: string }>
}

export function AppShell({
  children,
  searchQuery,
  onSearchChange,
}: {
  children: React.ReactNode
  searchQuery?: string
  onSearchChange?: (q: string) => void
}) {
  const { user, theme, toggleTheme, logout } = useAuth()
  const navigate = useNavigate()
  const [notifOpen, setNotifOpen] = useState(false)
  const [notifications, setNotifications] = useState<NotificationItem[]>([])

  const loadNotifs = async () => {
    try {
      const data = await apiRequest<NotificationItem[]>('/api/notifications')
      setNotifications(data)
    } catch {
      // ignore quietly
    }
  }

  useEffect(() => {
    loadNotifs()
  }, [])

  const markRead = async (id: number) => {
    try {
      await apiRequest(`/api/notifications/${id}/read`, { method: 'POST' })
      setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)))
    } catch {
      // ignore
    }
  }

  const unreadCount = notifications.filter((n) => !n.is_read).length

  const studentNav: NavItem[] = [
    { to: '/', label: 'Home', icon: LayoutDashboard },
    { to: '/performance', label: 'Insights', icon: TrendingUp },
    { to: '/careers', label: 'Careers', icon: Compass },
    { to: '/chat', label: 'Chat', icon: MessageSquareHeart },
    { to: '/planner', label: 'Planner', icon: CalendarDays },
    { to: '/wellbeing', label: 'Wellbeing', icon: HeartHandshake },
    { to: '/settings', label: 'Profile', icon: Settings },
  ]

  const mentorNav: NavItem[] = [
    { to: '/mentor', label: 'Students', icon: Users },
    { to: '/settings', label: 'Profile', icon: Settings },
  ]

  const adminNav: NavItem[] = [
    { to: '/admin', label: 'Admin', icon: ShieldCheck },
    { to: '/mentor', label: 'Mentoring', icon: Users },
    { to: '/settings', label: 'Profile', icon: Settings },
  ]

  const navItems =
    user?.role === 'admin' ? adminNav : user?.role === 'mentor' ? mentorNav : studentNav

  // Mobile bottom bar strictly 5 core items for students
  const mobileNav: NavItem[] =
    user?.role === 'student'
      ? [
          { to: '/', label: 'Home', icon: LayoutDashboard },
          { to: '/performance', label: 'Insights', icon: TrendingUp },
          { to: '/chat', label: 'Chat', icon: MessageSquareHeart },
          { to: '/planner', label: 'Planner', icon: CalendarDays },
          { to: '/settings', label: 'Profile', icon: Settings },
        ]
      : navItems

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <div className="flex min-h-screen">
        {/* Desktop Left Sidebar */}
        <aside
          aria-label="Primary navigation"
          className="hidden w-64 shrink-0 flex-col border-r border-slate-200 bg-white px-4 py-6 md:flex dark:border-slate-800 dark:bg-slate-900"
        >
          <div className="mb-8 flex items-center gap-3 px-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#4F46E5] text-white shadow-sm">
              <GraduationCap className="h-6 w-6" aria-hidden="true" />
            </div>
            <div>
              <span className="block font-['Poppins'] text-lg font-bold tracking-tight text-slate-900 dark:text-white">
                AdvisorAI
              </span>
              <span className="block text-xs font-medium text-slate-500 dark:text-slate-400">
                10th &amp; 12th Career Guide
              </span>
            </div>
          </div>

          <nav className="flex-1 space-y-1.5">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  className={({ isActive }) =>
                    `flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-base font-medium transition-colors ${
                      isActive
                        ? 'bg-[#4F46E5] text-white shadow-sm'
                        : 'text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
                    }`
                  }
                >
                  <Icon className="h-5 w-5 shrink-0" aria-hidden="true" />
                  <span>{item.label}</span>
                </NavLink>
              )
            })}
          </nav>

          {user?.role === 'student' && (
            <div className="mt-6 rounded-2xl bg-indigo-50 p-4 dark:bg-indigo-950/40">
              <div className="flex items-center gap-2 text-sm font-semibold text-[#4F46E5] dark:text-indigo-300">
                <BookOpen className="h-4 w-4" aria-hidden="true" />
                <span>{user.education_stage === '10th' ? 'Class 10th Track' : 'Class 12th Track'}</span>
              </div>
              <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">
                {user.stream || 'Personalized stream & career guidance active.'}
              </p>
            </div>
          )}

          <button
            type="button"
            onClick={() => {
              logout()
              navigate('/login')
            }}
            className="mt-4 flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-base font-medium text-rose-600 transition-colors hover:bg-rose-50 dark:text-rose-400 dark:hover:bg-rose-950/40"
          >
            <LogOut className="h-5 w-5" aria-hidden="true" />
            <span>Sign out</span>
          </button>
        </aside>

        {/* Main Column */}
        <div className="flex min-w-0 flex-1 flex-col pb-20 md:pb-0">
          {/* Top Bar */}
          <header className="sticky top-0 z-20 flex items-center justify-between gap-4 border-b border-slate-200 bg-white/90 px-4 py-3 backdrop-blur md:px-8 dark:border-slate-800 dark:bg-slate-900/90">
            <div className="flex items-center gap-3 md:hidden">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#4F46E5] text-white">
                <GraduationCap className="h-5 w-5" aria-hidden="true" />
              </div>
              <span className="font-['Poppins'] text-base font-bold">AdvisorAI</span>
            </div>

            <div className="relative hidden max-w-md flex-1 sm:block">
              <Search
                className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
                aria-hidden="true"
              />
              <input
                type="search"
                aria-label="Search AdvisorAI"
                value={searchQuery ?? ''}
                onChange={(e) => onSearchChange?.(e.target.value)}
                placeholder="Search subjects, careers, or students..."
                className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2 pl-10 pr-4 text-sm text-slate-800 placeholder:text-slate-400 focus:border-[#4F46E5] focus:bg-white focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
              />
            </div>

            <div className="flex items-center gap-2 sm:gap-3">
              <button
                type="button"
                onClick={toggleTheme}
                className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
              >
                {theme === 'light' ? (
                  <>
                    <Moon className="h-4 w-4" aria-hidden="true" />
                    <span className="hidden sm:inline">Dark</span>
                  </>
                ) : (
                  <>
                    <Sun className="h-4 w-4" aria-hidden="true" />
                    <span className="hidden sm:inline">Light</span>
                  </>
                )}
              </button>

              <div className="relative">
                <button
                  type="button"
                  onClick={() => {
                    setNotifOpen((o) => !o)
                    loadNotifs()
                  }}
                  className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
                >
                  <Bell className="h-4 w-4" aria-hidden="true" />
                  <span className="hidden sm:inline">Alerts</span>
                  {unreadCount > 0 && (
                    <span className="rounded-full bg-rose-600 px-1.5 py-0.5 text-xs font-bold text-white">
                      {unreadCount}
                    </span>
                  )}
                </button>

                {notifOpen && (
                  <div className="absolute right-0 mt-2 w-80 rounded-2xl border border-slate-200 bg-white p-4 shadow-xl dark:border-slate-700 dark:bg-slate-900">
                    <div className="mb-3 flex items-center justify-between">
                      <h3 className="text-base font-semibold">Notifications</h3>
                      <button
                        type="button"
                        onClick={() => setNotifOpen(false)}
                        className="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs font-medium text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"
                      >
                        <X className="h-3.5 w-3.5" aria-hidden="true" />
                        <span>Close</span>
                      </button>
                    </div>
                    {notifications.length === 0 ? (
                      <p className="py-4 text-center text-sm text-slate-500">
                        You&apos;re all caught up!
                      </p>
                    ) : (
                      <ul className="max-h-72 space-y-2 overflow-y-auto">
                        {notifications.map((n) => (
                          <li
                            key={n.id}
                            className={`rounded-xl border p-3 text-sm ${
                              n.is_read
                                ? 'border-slate-100 bg-slate-50/70 dark:border-slate-800 dark:bg-slate-800/40'
                                : 'border-indigo-200 bg-indigo-50/70 dark:border-indigo-900 dark:bg-indigo-950/40'
                            }`}
                          >
                            <div className="flex items-start justify-between gap-2">
                              <p className="font-semibold text-slate-900 dark:text-white">
                                {n.title}
                              </p>
                              {!n.is_read && (
                                <button
                                  type="button"
                                  onClick={() => markRead(n.id)}
                                  className="shrink-0 text-xs font-semibold text-[#4F46E5] hover:underline"
                                >
                                  Mark read
                                </button>
                              )}
                            </div>
                            <p className="mt-1 text-xs text-slate-600 dark:text-slate-300">
                              {n.message}
                            </p>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}
              </div>

              <button
                type="button"
                onClick={() => navigate('/settings')}
                className="inline-flex items-center gap-2 rounded-xl bg-slate-100 px-3 py-1.5 text-sm font-semibold text-slate-800 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-100"
              >
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[#4F46E5] text-xs font-bold text-white">
                  {user?.full_name?.[0]?.toUpperCase() || 'A'}
                </span>
                <span className="hidden md:inline">{user?.full_name?.split(' ')[0]}</span>
              </button>
            </div>
          </header>

          {/* Main Content */}
          <main className="mx-auto w-full max-w-7xl flex-1 p-4 md:p-8">{children}</main>
        </div>
      </div>

      {/* Mobile Bottom Tab Bar */}
      <nav
        aria-label="Mobile navigation"
        className="fixed bottom-0 left-0 right-0 z-30 flex items-center justify-around border-t border-slate-200 bg-white px-2 py-2 md:hidden dark:border-slate-800 dark:bg-slate-900"
      >
        {mobileNav.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex flex-col items-center gap-1 rounded-xl px-3 py-1 text-xs font-semibold ${
                  isActive ? 'text-[#4F46E5] dark:text-indigo-400' : 'text-slate-500 dark:text-slate-400'
                }`
              }
            >
              <Icon className="h-5 w-5" aria-hidden="true" />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>
    </div>
  )
}
