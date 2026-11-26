import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  CalendarClock,
  Compass,
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
      {showOnboarding && <OnboardingWizard onComplete={() => { setShowOnboarding(false); loadDashboard() }} />}

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
          {/* Greeting + Single Primary Action */}
          <div className="flex flex-col justify-between gap-4 rounded-2xl bg-gradient-to-r from-[#4F46E5] to-indigo-600 p-6 text-white shadow-md sm:flex-row sm:items-center">
            <div>
              <span className="inline-block rounded-full bg-white/20 px-3 py-1 text-xs font-semibold">
                {data.student.education_stage === '10th'
                  ? `Class 10th Pass-Out • ${data.student.board_name}`
                  : `Class 12th Pass-Out • ${data.student.stream}`}
              </span>
              <h1 className="mt-2 font-['Poppins'] text-2xl font-bold sm:text-3xl">
                {getGreeting()}, {firstName} 👋
              </h1>
              <p className="mt-1 text-base text-indigo-100">
                Today&apos;s focus: Keep your streak steady and review 1 weak topic before dinner.
              </p>
            </div>
            <button
              type="button"
              onClick={() => navigate('/chat')}
              className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-white px-5 py-3 text-base font-bold text-[#4F46E5] shadow-sm transition hover:bg-indigo-50"
            >
              <MessageSquareHeart className="h-5 w-5" aria-hidden="true" />
              <span>Ask Advisor</span>
            </button>
          </div>

          {/* 4 Summary Cards */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <Card>
              <div className="flex items-center justify-between text-sm font-semibold text-slate-500 dark:text-slate-400">
                <span>Current / Forecast CGPA</span>
                <GraduationCap className="h-5 w-5 text-[#4F46E5]" aria-hidden="true" />
              </div>
              <p className="mt-3 font-['Poppins'] text-3xl font-bold">
                {data.student.current_cgpa.toFixed(1)}{' '}
                <span className="text-base font-medium text-slate-400">/ 10</span>
              </p>
              <p className="mt-1 text-sm text-[#14B8A6] font-semibold">
                Next term forecast: {data.prediction.predicted_cgpa.toFixed(2)}
              </p>
            </Card>

            <Card>
              <div className="flex items-center justify-between text-sm font-semibold text-slate-500 dark:text-slate-400">
                <span>Attendance</span>
                <UserCheck className="h-5 w-5 text-[#14B8A6]" aria-hidden="true" />
              </div>
              <p className="mt-3 font-['Poppins'] text-3xl font-bold">
                {data.student.attendance_pct.toFixed(0)}%
              </p>
              <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                {data.student.attendance_pct >= 75
                  ? 'Safely above 75% target'
                  : 'Below 75% — attend next 3 classes'}
              </p>
            </Card>

            <Card>
              <div className="flex items-center justify-between text-sm font-semibold text-slate-500 dark:text-slate-400">
                <span>Risk Status</span>
                <TrendingUp className="h-5 w-5 text-slate-400" aria-hidden="true" />
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
                <CalendarClock className="h-5 w-5 text-amber-500" aria-hidden="true" />
              </div>
              <p className="mt-3 font-['Poppins'] text-3xl font-bold">
                {data.student.upcoming_deadlines_count}
              </p>
              <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                Mock tests &amp; assignments this month
              </p>
            </Card>
          </div>

          {/* Trend Chart + AI Insights */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <Card className="lg:col-span-2">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h2 className="font-['Poppins'] text-lg font-bold">Performance Trend</h2>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Your score progression from school boards to current term
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => navigate('/performance')}
                  className="text-sm font-semibold text-[#4F46E5] hover:underline"
                >
                  See prediction details
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
                      stroke="#4F46E5"
                      strokeWidth={3}
                      dot={{ r: 5, fill: '#14B8A6' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card>

            <Card className="flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 text-[#4F46E5] dark:text-indigo-400">
                  <Sparkles className="h-5 w-5" aria-hidden="true" />
                  <h2 className="font-['Poppins'] text-lg font-bold text-slate-900 dark:text-white">
                    Your AI Insights
                  </h2>
                </div>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  3 simple actions tailored for you today
                </p>

                <ul className="mt-4 space-y-3">
                  {data.prediction.ai_insights.map((tip, idx) => (
                    <li
                      key={idx}
                      className="rounded-xl bg-slate-50 p-3.5 text-sm leading-relaxed text-slate-700 dark:bg-slate-800/70 dark:text-slate-200"
                    >
                      <span className="mr-2 font-bold text-[#4F46E5]">{idx + 1}.</span>
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
              className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-[#4F46E5] dark:border-slate-800 dark:bg-slate-900"
            >
              <div className="rounded-xl bg-indigo-50 p-3 text-[#4F46E5] dark:bg-indigo-950">
                <MessageSquareHeart className="h-5 w-5" aria-hidden="true" />
              </div>
              <div>
                <p className="text-base font-bold">Ask Advisor</p>
                <p className="text-sm text-slate-500">Get instant answers on CGPA &amp; streams</p>
              </div>
            </button>

            <button
              type="button"
              onClick={() => navigate('/planner')}
              className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-[#14B8A6] dark:border-slate-800 dark:bg-slate-900"
            >
              <div className="rounded-xl bg-teal-50 p-3 text-[#14B8A6] dark:bg-teal-950">
                <CalendarClock className="h-5 w-5" aria-hidden="true" />
              </div>
              <div>
                <p className="text-base font-bold">Open Study Plan</p>
                <p className="text-sm text-slate-500">Weekly schedule built around weak areas</p>
              </div>
            </button>

            <button
              type="button"
              onClick={() => navigate('/careers')}
              className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-[#4F46E5] dark:border-slate-800 dark:bg-slate-900"
            >
              <div className="rounded-xl bg-indigo-50 p-3 text-[#4F46E5] dark:bg-indigo-950">
                <Compass className="h-5 w-5" aria-hidden="true" />
              </div>
              <div>
                <p className="text-base font-bold">View Careers</p>
                <p className="text-sm text-slate-500">Top career &amp; course matches after 10th/12th</p>
              </div>
            </button>
          </div>
        </motion.div>
      )}
    </AppShell>
  )
}
