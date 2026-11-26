import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Award, BookOpen, Compass, MessageSquareHeart, Sparkles } from 'lucide-react'
import { AppShell } from '../components/AppShell'
import { Card, DashboardSkeleton, ErrorBanner } from '../components/ui'
import { apiRequest } from '../lib/api'
import { CareersResponse } from '../types'

export function CareerGuidancePage() {
  const navigate = useNavigate()
  const [data, setData] = useState<CareersResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await apiRequest<CareersResponse>('/api/student/careers')
      setData(res)
    } catch {
      setError('Unable to load career recommendations right now.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <AppShell>
      {loading ? (
        <DashboardSkeleton />
      ) : error || !data ? (
        <ErrorBanner message={error || 'Unable to load'} onRetry={load} />
      ) : (
        <div className="space-y-6">
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div>
              <h1 className="font-['Poppins'] text-2xl font-bold">Career &amp; Stream Guidance</h1>
              <p className="mt-1 text-base text-slate-600 dark:text-slate-300">
                Top 3 career matches for your {data.education_stage} profile, plus skills &amp; starter courses.
              </p>
            </div>
            <button
              type="button"
              onClick={() => navigate('/chat')}
              className="inline-flex items-center gap-2 rounded-xl bg-[#4F46E5] px-5 py-3 text-base font-semibold text-white hover:bg-[#4338CA]"
            >
              <MessageSquareHeart className="h-5 w-5" aria-hidden="true" />
              <span>Discuss with Advisor</span>
            </button>
          </div>

          {/* 10th Pass-Out Stream Banner */}
          {data.stream_recommendation && (
            <div className="rounded-2xl border border-teal-200 bg-teal-50 p-5 dark:border-teal-900 dark:bg-teal-950/40">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2 text-teal-800 dark:text-teal-300">
                  <Sparkles className="h-5 w-5" aria-hidden="true" />
                  <span className="text-sm font-bold uppercase tracking-wide">
                    Best Class 11–12 Stream for You
                  </span>
                </div>
                <span className="rounded-full bg-teal-600 px-3 py-1 text-xs font-bold text-white">
                  {data.stream_recommendation.match_pct}% Match
                </span>
              </div>
              <h2 className="mt-2 font-['Poppins'] text-xl font-bold text-slate-900 dark:text-white">
                {data.stream_recommendation.title}
              </h2>
              <p className="mt-1 text-base text-slate-700 dark:text-slate-200">
                {data.stream_recommendation.summary}
              </p>
            </div>
          )}

          {/* Top 3 Career Cards */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {data.careers.map((career, idx) => (
              <Card key={career.id} className="flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between gap-3">
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-indigo-50 px-3 py-1 text-xs font-bold text-[#4F46E5] dark:bg-indigo-950 dark:text-indigo-300">
                      <Compass className="h-3.5 w-3.5" aria-hidden="true" />
                      #{idx + 1} Match
                    </span>
                    <span className="rounded-full bg-emerald-50 px-3 py-1 text-sm font-bold text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                      {career.match_pct}% fit
                    </span>
                  </div>

                  <h2 className="mt-4 font-['Poppins'] text-xl font-bold">{career.title}</h2>
                  <p className="mt-2 text-sm leading-relaxed text-slate-600 dark:text-slate-300">
                    {career.summary}
                  </p>

                  {/* Skill-Gap Progress Bars */}
                  <div className="mt-5">
                    <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">
                      Skill Gaps to Close
                    </h3>
                    <div className="mt-3 space-y-3">
                      {career.skill_gaps.map((sg) => (
                        <div key={sg.skill}>
                          <div className="flex justify-between text-xs font-semibold">
                            <span>{sg.skill}</span>
                            <span className="text-slate-500">
                              You: {sg.current}% / Goal: {sg.target}%
                            </span>
                          </div>
                          <div className="relative mt-1.5 h-2.5 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                            <div
                              className="h-full rounded-full bg-[#4F46E5]"
                              style={{ width: `${sg.current}%` }}
                            />
                            <div
                              className="absolute top-0 bottom-0 w-0.5 bg-amber-500"
                              style={{ left: `${sg.target}%` }}
                              title={`Target: ${sg.target}%`}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Suggested Courses & Projects */}
                <div className="mt-6 border-t border-slate-100 pt-4 dark:border-slate-800">
                  <h3 className="flex items-center gap-1.5 text-sm font-bold text-slate-800 dark:text-slate-200">
                    <BookOpen className="h-4 w-4 text-[#14B8A6]" aria-hidden="true" />
                    <span>Recommended Next Steps</span>
                  </h3>
                  <ul className="mt-2.5 space-y-2">
                    {career.suggested_courses.map((course) => (
                      <li
                        key={course.title}
                        className="flex items-start justify-between gap-2 rounded-xl bg-slate-50 p-2.5 text-xs dark:bg-slate-800/70"
                      >
                        <div>
                          <p className="font-semibold text-slate-900 dark:text-white">
                            {course.title}
                          </p>
                          <p className="text-slate-500">
                            {course.provider} • {course.duration}
                          </p>
                        </div>
                        <span className="inline-flex shrink-0 items-center gap-1 rounded-md bg-white px-2 py-0.5 font-semibold text-[#4F46E5] shadow-sm dark:bg-slate-700 dark:text-indigo-300">
                          <Award className="h-3 w-3" aria-hidden="true" />
                          {course.type}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </AppShell>
  )
}
