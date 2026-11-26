import React, { useEffect, useState } from 'react'
import { CheckSquare, GripVertical, RefreshCw, Square } from 'lucide-react'
import { AppShell } from '../components/AppShell'
import { Card, DashboardSkeleton, ErrorBanner } from '../components/ui'
import { apiRequest } from '../lib/api'
import { StudyTask } from '../types'

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

function ProgressRing({ pct }: { pct: number }) {
  const r = 28
  const c = 2 * Math.PI * r
  const offset = c - (pct / 100) * c
  return (
    <div className="flex items-center gap-3">
      <svg width="70" height="70" viewBox="0 0 70 70" aria-label={`Weekly progress ${pct}%`}>
        <circle
          cx="35"
          cy="35"
          r={r}
          fill="none"
          stroke="currentColor"
          strokeWidth="7"
          className="text-slate-200 dark:text-slate-800"
        />
        <circle
          cx="35"
          cy="35"
          r={r}
          fill="none"
          stroke="#14B8A6"
          strokeWidth="7"
          strokeDasharray={c}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 35 35)"
        />
        <text
          x="35"
          y="40"
          textAnchor="middle"
          className="fill-slate-900 text-sm font-bold dark:fill-white"
        >
          {pct}%
        </text>
      </svg>
      <div>
        <p className="text-sm font-bold">Weekly Progress</p>
        <p className="text-xs text-slate-500">Drag tasks to reschedule</p>
      </div>
    </div>
  )
}

export function StudyPlannerPage() {
  const [tasks, setTasks] = useState<StudyTask[]>([])
  const [loading, setLoading] = useState(true)
  const [regenBusy, setRegenBusy] = useState(false)
  const [draggedId, setDraggedId] = useState<number | null>(null)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await apiRequest<StudyTask[]>('/api/student/study-plan')
      setTasks(data)
    } catch {
      setError('Could not load your study planner.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const regenerate = async () => {
    setRegenBusy(true)
    try {
      const data = await apiRequest<StudyTask[]>('/api/student/study-plan/regenerate', {
        method: 'POST',
      })
      setTasks(data)
    } finally {
      setRegenBusy(false)
    }
  }

  const toggleComplete = async (task: StudyTask) => {
    const next = !task.completed
    setTasks((prev) => prev.map((t) => (t.id === task.id ? { ...t, completed: next } : t)))
    await apiRequest(`/api/student/study-plan/${task.id}`, {
      method: 'PATCH',
      body: JSON.stringify({ completed: next }),
    })
  }

  const moveToDay = async (taskId: number, targetDay: string) => {
    setTasks((prev) => prev.map((t) => (t.id === taskId ? { ...t, day_of_week: targetDay } : t)))
    await apiRequest(`/api/student/study-plan/${taskId}`, {
      method: 'PATCH',
      body: JSON.stringify({ day_of_week: targetDay }),
    })
  }

  const completedCount = tasks.filter((t) => t.completed).length
  const pct = tasks.length ? Math.round((completedCount / tasks.length) * 100) : 0

  return (
    <AppShell>
      {loading ? (
        <DashboardSkeleton />
      ) : error ? (
        <ErrorBanner message={error} onRetry={load} />
      ) : (
        <div className="space-y-6">
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div>
              <h1 className="font-['Poppins'] text-2xl font-bold">Weekly Study Planner</h1>
              <p className="mt-1 text-base text-slate-600 dark:text-slate-300">
                Auto-built from your weak subjects and upcoming exam dates. Drag any task to another day.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-4">
              <ProgressRing pct={pct} />
              <button
                type="button"
                onClick={regenerate}
                disabled={regenBusy}
                className="inline-flex items-center gap-2 rounded-xl bg-[#4F46E5] px-5 py-3 text-base font-semibold text-white hover:bg-[#4338CA] disabled:opacity-60"
              >
                <RefreshCw className={`h-5 w-5 ${regenBusy ? 'animate-spin' : ''}`} aria-hidden="true" />
                <span>{regenBusy ? 'Building...' : 'Regenerate plan'}</span>
              </button>
            </div>
          </div>

          {/* 7-Day Calendar Grid */}
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
            {DAYS.map((day) => {
              const dayTasks = tasks.filter((t) => t.day_of_week === day)
              return (
                <Card
                  key={day}
                  className="flex min-h-[220px] flex-col p-4"
                >
                  <div
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={() => {
                      if (draggedId !== null) {
                        moveToDay(draggedId, day)
                        setDraggedId(null)
                      }
                    }}
                    className="flex flex-1 flex-col"
                  >
                    <div className="mb-3 flex items-center justify-between border-b border-slate-100 pb-2 dark:border-slate-800">
                      <h2 className="font-['Poppins'] text-base font-bold">{day}</h2>
                      <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                        {dayTasks.length} tasks
                      </span>
                    </div>

                    {dayTasks.length === 0 ? (
                      <div className="flex flex-1 items-center justify-center rounded-xl border border-dashed border-slate-200 p-4 text-center text-sm text-slate-400 dark:border-slate-700">
                        Drop a study task here
                      </div>
                    ) : (
                      <div className="space-y-2.5">
                        {dayTasks.map((task) => (
                          <div
                            key={task.id}
                            draggable
                            onDragStart={() => setDraggedId(task.id)}
                            className={`cursor-grab rounded-xl border p-3 transition ${
                              task.completed
                                ? 'border-emerald-200 bg-emerald-50/50 opacity-75 dark:border-emerald-900 dark:bg-emerald-950/30'
                                : 'border-slate-200 bg-slate-50/80 hover:border-[#4F46E5] dark:border-slate-700 dark:bg-slate-800/70'
                            }`}
                          >
                            <div className="flex items-start gap-2">
                              <button
                                type="button"
                                onClick={() => toggleComplete(task)}
                                aria-label={`Mark ${task.subject} task complete`}
                                className="mt-0.5 text-[#4F46E5]"
                              >
                                {task.completed ? (
                                  <CheckSquare className="h-5 w-5 text-emerald-600" />
                                ) : (
                                  <Square className="h-5 w-5" />
                                )}
                              </button>
                              <div className="min-w-0 flex-1">
                                <div className="flex items-center justify-between gap-1">
                                  <p
                                    className={`text-sm font-bold ${
                                      task.completed ? 'line-through text-slate-400' : ''
                                    }`}
                                  >
                                    {task.subject}
                                  </p>
                                  <GripVertical className="h-4 w-4 shrink-0 text-slate-400" aria-hidden="true" />
                                </div>
                                <p className="mt-0.5 text-xs text-slate-600 dark:text-slate-300">
                                  {task.topic}
                                </p>
                                <div className="mt-2 flex items-center justify-between text-xs">
                                  <span className="font-semibold text-slate-500">
                                    {task.duration_minutes} mins
                                  </span>
                                  <span
                                    className={`rounded-full px-2 py-0.5 font-bold ${
                                      task.priority === 'high'
                                        ? 'bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300'
                                        : task.priority === 'medium'
                                        ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                                        : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                                    }`}
                                  >
                                    {task.priority}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </Card>
              )
            })}
          </div>
        </div>
      )}
    </AppShell>
  )
}
