import React, { useEffect, useState } from 'react'
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { HelpCircle, SlidersHorizontal, ThumbsDown, ThumbsUp } from 'lucide-react'
import { AppShell } from '../components/AppShell'
import { Card, DashboardSkeleton, ErrorBanner, RiskBadge } from '../components/ui'
import { apiRequest } from '../lib/api'
import { ExplainFactor, StudentDashboardData } from '../types'

function CgpaGauge({ value }: { value: number }) {
  const pct = Math.min(100, Math.max(0, (value / 10) * 100))
  const radius = 64
  const circumference = Math.PI * radius
  const dashOffset = circumference - (pct / 100) * circumference

  return (
    <div className="flex flex-col items-center">
      <svg width="170" height="105" viewBox="0 0 170 105" aria-label={`Predicted CGPA ${value} out of 10`}>
        <path
          d="M 21 90 A 64 64 0 0 1 149 90"
          fill="none"
          stroke="currentColor"
          strokeWidth="14"
          className="text-slate-200 dark:text-slate-800"
          strokeLinecap="round"
        />
        <path
          d="M 21 90 A 64 64 0 0 1 149 90"
          fill="none"
          stroke="#7B2D8E"
          strokeWidth="14"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          strokeLinecap="round"
          className="transition-all duration-500"
        />
        <text
          x="85"
          y="74"
          textAnchor="middle"
          className="fill-slate-900 font-['Poppins'] text-2xl font-bold dark:fill-white"
        >
          {value.toFixed(2)}
        </text>
        <text x="85" y="94" textAnchor="middle" className="fill-slate-500 text-xs font-medium">
          out of 10.0
        </text>
      </svg>
    </div>
  )
}

export function PerformancePage() {
  const [data, setData] = useState<StudentDashboardData | null>(null)
  const [simPred, setSimPred] = useState<{
    predicted_cgpa: number
    pass_probability: number
    risk_level: string
    top_reasons: ExplainFactor[]
  } | null>(null)
  const [sim, setSim] = useState({
    attendance_pct: 84,
    internal_marks_avg: 78,
    assignment_score_avg: 80,
    past_cgpa: 8.1,
    study_hours_per_week: 20,
  })
  const [loading, setLoading] = useState(true)
  const [simulating, setSimulating] = useState(false)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await apiRequest<StudentDashboardData>('/api/student/dashboard')
      setData(res)
      setSim({
        attendance_pct: res.student.attendance_pct,
        internal_marks_avg: res.student.internal_marks_avg,
        assignment_score_avg: res.student.assignment_score_avg,
        past_cgpa: res.student.current_cgpa,
        study_hours_per_week: res.student.study_hours_per_week,
      })
      setSimPred(res.prediction)
    } catch {
      setError('Could not load your performance forecast.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const runSimulation = async () => {
    setSimulating(true)
    try {
      const res = await apiRequest<{
        predicted_cgpa: number
        pass_probability: number
        risk_level: string
        top_reasons: ExplainFactor[]
      }>('/api/student/predict/simulate', {
        method: 'POST',
        body: JSON.stringify(sim),
      })
      setSimPred(res)
    } finally {
      setSimulating(false)
    }
  }

  const activePred = simPred || data?.prediction

  return (
    <AppShell>
      {loading ? (
        <DashboardSkeleton />
      ) : error || !data || !activePred ? (
        <ErrorBanner message={error || 'Data unavailable'} onRetry={load} />
      ) : (
        <div className="space-y-6">
          <div className="rounded-2xl bg-gradient-to-r from-[#7B2D8E] to-[#581C68] p-6 text-white shadow-md">
            <h1 className="font-['Poppins'] text-2xl font-bold">Score Forecast &amp; Insights</h1>
            <p className="mt-1 text-base text-purple-100">
              See where your grades are heading, which subjects shine, and what you can tweak today.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <Card className="flex flex-col items-center justify-between text-center">
              <div className="w-full">
                <h2 className="font-['Poppins'] text-lg font-bold">Predicted Next CGPA</h2>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Based on attendance, internal tests &amp; study hours
                </p>
              </div>
              <div className="my-4">
                <CgpaGauge value={activePred.predicted_cgpa} />
              </div>
              <div className="space-y-2">
                <RiskBadge risk={activePred.risk_level} />
                <p className="text-sm font-medium text-slate-600 dark:text-slate-300">
                  Pass likelihood: <span className="font-bold">{activePred.pass_probability}%</span>
                </p>
              </div>
            </Card>

            <Card className="lg:col-span-2">
              <h2 className="font-['Poppins'] text-lg font-bold">Subject-wise Scorecard</h2>
              <p className="mb-4 text-sm text-slate-500 dark:text-slate-400">
                Compare internal test marks, assignments, and attendance per subject
              </p>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.subject_scores}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="subject" tick={{ fontSize: 12 }} />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="internal" name="Internal %" fill="#7B2D8E" radius={[6, 6, 0, 0]} />
                    <Bar dataKey="assignment" name="Assignments %" fill="#FF6B4A" radius={[6, 6, 0, 0]} />
                    <Bar dataKey="attendance" name="Attendance %" fill="#14B8A6" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </div>

          <Card>
            <div className="flex items-center gap-2">
              <HelpCircle className="h-5 w-5 text-[#7B2D8E]" aria-hidden="true" />
              <h2 className="font-['Poppins'] text-lg font-bold">Why this prediction?</h2>
            </div>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Here are the top habits and scores shaping your forecast in simple words.
            </p>

            <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
              {activePred.top_reasons.map((item) => {
                const positive = item.direction === 'positive'
                return (
                  <div
                    key={item.key}
                    className="rounded-xl border border-purple-100 bg-[#FAF7FD] p-4 dark:border-slate-800 dark:bg-slate-800/50"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        {positive ? (
                          <ThumbsUp className="h-4 w-4 text-emerald-600" aria-hidden="true" />
                        ) : (
                          <ThumbsDown className="h-4 w-4 text-rose-600" aria-hidden="true" />
                        )}
                        <span className="text-sm font-bold">{item.factor}</span>
                      </div>
                      <span
                        className={`text-xs font-bold ${
                          positive ? 'text-emerald-600' : 'text-rose-600'
                        }`}
                      >
                        {item.impact}% impact
                      </span>
                    </div>
                    <div className="mt-2 h-2.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                      <div
                        className={`h-full rounded-full ${
                          positive ? 'bg-emerald-500' : 'bg-rose-500'
                        }`}
                        style={{ width: `${Math.min(100, item.impact * 2.2)}%` }}
                      />
                    </div>
                    <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
                      {item.plain_text}
                    </p>
                  </div>
                )
              })}
            </div>
          </Card>

          <Card>
            <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
              <div>
                <div className="flex items-center gap-2">
                  <SlidersHorizontal className="h-5 w-5 text-[#FF6B4A]" aria-hidden="true" />
                  <h2 className="font-['Poppins'] text-lg font-bold">Test Your Score (What-If)</h2>
                </div>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  Slide to see how boosting attendance or extra weekly study hours lifts your forecast.
                </p>
              </div>
              <button
                type="button"
                onClick={runSimulation}
                disabled={simulating}
                className="rounded-xl bg-gradient-to-r from-[#FF7A45] to-[#FF5163] px-5 py-3 text-base font-bold text-white shadow-sm hover:brightness-105 disabled:opacity-60"
              >
                {simulating ? 'Calculating...' : 'Update Forecast'}
              </button>
            </div>

            <div className="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
              <label className="block">
                <span className="flex justify-between text-sm font-semibold">
                  <span>Attendance</span>
                  <span className="text-[#7B2D8E]">{sim.attendance_pct}%</span>
                </span>
                <input
                  type="range"
                  min={40}
                  max={100}
                  value={sim.attendance_pct}
                  onChange={(e) => setSim({ ...sim, attendance_pct: Number(e.target.value) })}
                  className="mt-2 w-full accent-[#7B2D8E]"
                />
              </label>

              <label className="block">
                <span className="flex justify-between text-sm font-semibold">
                  <span>Internal Marks</span>
                  <span className="text-[#7B2D8E]">{sim.internal_marks_avg}%</span>
                </span>
                <input
                  type="range"
                  min={30}
                  max={100}
                  value={sim.internal_marks_avg}
                  onChange={(e) => setSim({ ...sim, internal_marks_avg: Number(e.target.value) })}
                  className="mt-2 w-full accent-[#7B2D8E]"
                />
              </label>

              <label className="block">
                <span className="flex justify-between text-sm font-semibold">
                  <span>Assignments</span>
                  <span className="text-[#7B2D8E]">{sim.assignment_score_avg}%</span>
                </span>
                <input
                  type="range"
                  min={30}
                  max={100}
                  value={sim.assignment_score_avg}
                  onChange={(e) => setSim({ ...sim, assignment_score_avg: Number(e.target.value) })}
                  className="mt-2 w-full accent-[#7B2D8E]"
                />
              </label>

              <label className="block">
                <span className="flex justify-between text-sm font-semibold">
                  <span>Study Hours / wk</span>
                  <span className="text-[#14B8A6]">{sim.study_hours_per_week} hrs</span>
                </span>
                <input
                  type="range"
                  min={4}
                  max={45}
                  value={sim.study_hours_per_week}
                  onChange={(e) => setSim({ ...sim, study_hours_per_week: Number(e.target.value) })}
                  className="mt-2 w-full accent-[#14B8A6]"
                />
              </label>
            </div>
          </Card>
        </div>
      )}
    </AppShell>
  )
}
