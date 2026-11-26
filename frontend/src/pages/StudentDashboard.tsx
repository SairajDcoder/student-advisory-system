import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  CalendarClock,
  Compass,
  Flame,
  GraduationCap,
  MessageSquareHeart,
  Sparkles,
  TrendingUp,
  UserCheck,
} from 'lucide-react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { AppShell } from '../components/AppShell'
import { OnboardingWizard } from '../components/OnboardingWizard'
import { Card, DashboardSkeleton, ErrorBanner, RiskBadge } from '../components/ui'
import { apiRequest } from '../lib/api'
import { StudentDashboardData } from '../types'

function getGreeting() {
  const hr = new Date().getHours()
  if (hr < 12) return 'Good morning'
  if (hr < 17) return 'Good afternoon'
  return 'Good evening'
}

export function StudentDashboard() {
  const navigate = useNavigate()
  const [data, setData] = useState<StudentDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showOnboarding, setShowOnboarding] = useState(false)

  const loadDashboard = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await apiRequest<StudentDashboardData>('/api/student/dashboard')
      setData(res)
      if (!res.student.onboarding_completed) {
        setShowOnboarding(true)
      }
    } catch {
      setError('We could not load your dashboard right now. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDashboard()
  }, [])

  const firstName = data?.student.full_name.split(' ')[0] || 'Student'

  return (
    <AppShell>
      {showOnboarding && (
        <OnboardingWizard
          onComplete={() => {
            setShowOnboarding(false)
            loadDashboard()
          }}
        />
      )}

      {loading ? (
        <DashboardSkeleton />
      ) : error || !data ? (
        <ErrorBanner message={error || 'Unable to load dashboard'} onRetry={loadDashboard} />
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
          className="space-y-6"
        >
          {/* BYJU'S-inspired Purple Teen Hero Banner */}
          <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#883898] via-[#7B2D8E] to-[#581C68] p-6 text-white shadow-lg sm:p-7">
            <div className="pointer-events-none absolute -right-10 -top-10 h-44 w-44 rounded-full bg-white/10" />
            <div className="pointer-events-none absolute bottom-3 right-56 hidden h-10 w-10 items-center justify-center rounded-full bg-[#FFD166] text-xs font-extrabold text-slate-900 shadow md:flex">
              π
            </div>
            <div className="relative z-10 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
              <div>
                <div className="inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1 text-xs font-bold text-amber-200">
                  <Flame className="h-3.5 w-3.5" aria-hidden="true" />
                  <span>
                    {data.student.education_stage === '10th'
                      ? `Class 10th Pass-Out • ${data.student.board_name}`
                      : `Class 12th Pass-Out • ${data.student.stream}`}
                  </span>
                </div>
                <h1 className="mt-2 font-['Poppins'] text-2xl font-bold sm:text-3xl">
                  {getGreeting()}, {firstName}! Ready to level up?
                </h1>
                <p className="mt-1 text-base text-purple-100">
                  Today&apos;s focus: Knock out 1 study block and check your best career matches.
                </p>
              </div>
              <button
                type="button"
                onClick={() => navigate('/chat')}
                className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[#FF7A45] to-[#FF5163] px-6 py-3.5 text-base font-bold text-white shadow-md transition hover:brightness-105"
              >
                <MessageSquareHeart className="h-5 w-5" aria-hidden="true" />
                <span>Ask Advisor</span>
              </button>
            </div>
          </div>

          {/* 4 Summary Cards */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <Card>
              <div className="flex items-center justify-between text-sm font-semibold text-slate-500 dark:text-slate-400">
                <span>Current / Forecast CGPA</span>
                <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-purple-50 text-[#7B2D8E] dark:bg-purple-950">
                  <GraduationCap className="h-5 w-5" aria-hidden="true" />
                </span>
              </div>
              <p className="mt-3 font-['Poppins'] text-3xl font-bold">
                {data.student.current_cgpa.toFixed(1)}{' '}
                <span className="text-base font-medium text-slate-400">/ 10</span>
              </p>
              <p className="mt-1 text-sm font-bold text-[#7B2D8E] dark:text-purple-300">
                Next term forecast: {data.prediction.predicted_cgpa.toFixed(2)}
              </p>
            </Card>

            <Card>
              <div className="flex items-center justify-between text-sm font-semibold text-slate-500 dark:text-slate-400">
                <span>Attendance</span>
                <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-50 text-[#14B8A6] dark:bg-teal-950">
                  <UserCheck className="h-5 w-5" aria-hidden="true" />
                </span>
              </div>
              <p className="mt-3 font-['Poppins'] text-3xl font-bold">
                {data.student.attendance_pct.toFixed(0)}%
              </p>
              <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                {data.student.attendance_pct >= 75
                  ? 'Awesome — safely above 75%'
                  : 'Below 75% — attend next 3 classes'}
              </p>
            </Card>

            <Card>
              <div className="flex items-center justify-between text-sm font-semibold text-slate-500 dark:text-slate-400">
                <span>Risk Status</span>
                <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-100 text-slate-600 dark:bg-slate-800">
                  <TrendingUp className="h-5 w-5" aria-hidden="true" />
                </span>
              </div>
              <div className="mt-3">
                <RiskBadge risk={data.prediction.risk_level} />
              </div>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
                Pass confidence: {data.prediction.pass_probability}%
              </p>
            </Card>

            <Card>
              <div className="flex items-center justify-between text-sm font-semibold text-slate-500 dark:text-slate-400">
                <span>Upcoming Deadlines</span>
                <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-orange-50 text-[#FF6B4A] dark:bg-orange-950">
                  <CalendarClock className="h-5 w-5" aria-hidden="true" />
                </span>
              </div>
              <p className="mt-3 font-['Poppins'] text-3xl font-bold">
                {data.student.upcoming_deadlines_count}
              </p>
              <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                Tests &amp; assignments this month
              </p>
            </Card>
          </div>

          {/* Trend Chart + AI Insights */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <Card className="lg:col-span-2">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h2 className="font-['Poppins'] text-lg font-bold">Your Score Journey</h2>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    How your marks &amp; CGPA are trending toward your goal
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => navigate('/performance')}
                  className="text-sm font-bold text-[#7B2D8E] hover:underline dark:text-purple-300"
                >
                  See prediction details →
                </button>
              </div>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={[
                      ...data.student.previous_grades,
                      { term: 'Predicted', cgpa: data.prediction.predicted_cgpa },
                    ]}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="term" tick={{ fontSize: 12 }} />
                    <YAxis domain={[4, 10]} tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="cgpa"
                      stroke="#7B2D8E"
                      strokeWidth={3}
                      dot={{ r: 5, fill: '#FF6B4A' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card>

            <Card className="flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 text-[#7B2D8E] dark:text-purple-300">
                  <Sparkles className="h-5 w-5" aria-hidden="true" />
                  <h2 className="font-['Poppins'] text-lg font-bold text-slate-900 dark:text-white">
                    Smart Tips for You
                  </h2>
                </div>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  3 quick wins to boost your score
                </p>

                <ul className="mt-4 space-y-3">
                  {data.prediction.ai_insights.map((tip, idx) => (
                    <li
                      key={idx}
                      className="rounded-xl border border-purple-100/80 bg-[#FAF7FD] p-3.5 text-sm leading-relaxed text-slate-700 dark:border-slate-800 dark:bg-slate-800/70 dark:text-slate-200"
                    >
                      <span className="mr-2 font-extrabold text-[#FF6B4A]">{idx + 1}.</span>
                      {tip}
                    </li>
                  ))}
                </ul>
              </div>

              {data.student.mentor_remarks && (
                <div className="mt-4 rounded-xl border border-teal-200 bg-teal-50/70 p-3 text-xs text-teal-900 dark:border-teal-900 dark:bg-teal-950/40 dark:text-teal-200">
                  <span className="font-bold">Mentor Note: </span>
                  {data.student.mentor_remarks}
                </div>
              )}
            </Card>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <button
              type="button"
              onClick={() => navigate('/chat')}
              className="flex items-center gap-3 rounded-2xl border border-purple-100 bg-white p-4 text-left shadow-sm transition hover:border-[#7B2D8E] dark:border-slate-800 dark:bg-slate-900"
            >
              <div className="rounded-xl bg-purple-50 p-3 text-[#7B2D8E] dark:bg-purple-950">
                <MessageSquareHeart className="h-5 w-5" aria-hidden="true" />
              </div>
              <div>
                <p className="text-base font-bold">Ask Advisor</p>
                <p className="text-sm text-slate-500">Get instant help on streams &amp; exams</p>
              </div>
            </button>

            <button
              type="button"
              onClick={() => navigate('/planner')}
              className="flex items-center gap-3 rounded-2xl border border-purple-100 bg-white p-4 text-left shadow-sm transition hover:border-[#14B8A6] dark:border-slate-800 dark:bg-slate-900"
            >
              <div className="rounded-xl bg-teal-50 p-3 text-[#14B8A6] dark:bg-teal-950">
                <CalendarClock className="h-5 w-5" aria-hidden="true" />
              </div>
              <div>
                <p className="text-base font-bold">Open Study Plan</p>
                <p className="text-sm text-slate-500">Weekly schedule built for your weak areas</p>
              </div>
            </button>

            <button
              type="button"
              onClick={() => navigate('/careers')}
              className="flex items-center gap-3 rounded-2xl border border-purple-100 bg-white p-4 text-left shadow-sm transition hover:border-[#FF6B4A] dark:border-slate-800 dark:bg-slate-900"
            >
              <div className="rounded-xl bg-orange-50 p-3 text-[#FF6B4A] dark:bg-orange-950">
                <Compass className="h-5 w-5" aria-hidden="true" />
              </div>
              <div>
                <p className="text-base font-bold">View Careers</p>
                <p className="text-sm text-slate-500">Top career &amp; stream matches for you</p>
              </div>
            </button>
          </div>
        </motion.div>
      )}
    </AppShell>
  )
}
