import React, { useEffect, useState } from 'react'
import { CalendarPlus, Eye, MessageSquarePlus, Search, X } from 'lucide-react'
import { AppShell } from '../components/AppShell'
import { Card, DashboardSkeleton, ErrorBanner, RiskBadge } from '../components/ui'
import { apiRequest } from '../lib/api'
import { MentorStudent } from '../types'

export function MentorDashboard() {
  const [students, setStudents] = useState<MentorStudent[]>([])
  const [search, setSearch] = useState('')
  const [riskFilter, setRiskFilter] = useState<'All' | 'High' | 'Medium' | 'Low'>('All')
  const [selected, setSelected] = useState<MentorStudent | null>(null)
  const [remarks, setRemarks] = useState('')
  const [meetingAt, setMeetingAt] = useState('')
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await apiRequest<MentorStudent[]>('/api/mentor/students')
      setStudents(data)
    } catch {
      setError('Unable to load assigned students.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const openDrawer = (st: MentorStudent) => {
    setSelected(st)
    setRemarks(st.mentor_remarks || '')
    setMeetingAt(st.next_meeting_at || '')
    setToast('')
  }

  const saveMentorAction = async (scheduleOnly = false) => {
    if (!selected) return
    setSaving(true)
    setToast('')
    try {
      const res = await apiRequest<{
        student_id: number
        mentor_remarks: string
        next_meeting_at: string
      }>(`/api/mentor/students/${selected.student_id}/remarks`, {
        method: 'POST',
        body: JSON.stringify({
          remarks: remarks || 'Reviewed student progress.',
          next_meeting_at: scheduleOnly || meetingAt ? meetingAt || 'Friday, 4:30 PM' : undefined,
        }),
      })
      setStudents((prev) =>
        prev.map((s) =>
          s.student_id === selected.student_id
            ? { ...s, mentor_remarks: res.mentor_remarks, next_meeting_at: res.next_meeting_at }
            : s
        )
      )
      setSelected((prev) =>
        prev
          ? { ...prev, mentor_remarks: res.mentor_remarks, next_meeting_at: res.next_meeting_at }
          : null
      )
      setToast(scheduleOnly ? 'Meeting scheduled and student notified!' : 'Mentor remarks saved!')
    } finally {
      setSaving(false)
    }
  }

  const filtered = students.filter((s) => {
    const matchText =
      s.full_name.toLowerCase().includes(search.toLowerCase()) ||
      s.department.toLowerCase().includes(search.toLowerCase())
    const matchRisk = riskFilter === 'All' || s.risk_level === riskFilter
    return matchText && matchRisk
  })

  return (
    <AppShell searchQuery={search} onSearchChange={setSearch}>
      {loading ? (
        <DashboardSkeleton />
      ) : error ? (
        <ErrorBanner message={error} onRetry={load} />
      ) : (
        <div className="space-y-6">
          <div>
            <h1 className="font-['Poppins'] text-2xl font-bold">Mentor Advisory Portal</h1>
            <p className="mt-1 text-base text-slate-600 dark:text-slate-300">
              Monitor 10th &amp; 12th students, review AI risk alerts, add remarks, and schedule 1-on-1s.
            </p>
          </div>

          {/* Search & Risk Filter */}
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div className="relative flex-1 max-w-md">
              <Search
                className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
                aria-hidden="true"
              />
              <input
                type="search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Filter by student name or stream..."
                className="w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-base dark:border-slate-700 dark:bg-slate-900"
              />
            </div>

            <div className="flex flex-wrap gap-2">
              {(['All', 'High', 'Medium', 'Low'] as const).map((level) => (
                <button
                  key={level}
                  type="button"
                  onClick={() => setRiskFilter(level)}
                  className={`rounded-xl px-4 py-2 text-sm font-semibold transition ${
                    riskFilter === level
                      ? 'bg-[#4F46E5] text-white'
                      : 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200'
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          {/* Student List */}
          <Card className="overflow-x-auto p-0">
            <table className="w-full min-w-[680px] text-left">
              <thead className="border-b border-slate-200 bg-slate-50 text-xs font-bold uppercase text-slate-500 dark:border-slate-800 dark:bg-slate-800/60 dark:text-slate-300">
                <tr>
                  <th className="px-6 py-4">Student</th>
                  <th className="px-6 py-4">Stage / Track</th>
                  <th className="px-6 py-4">CGPA (Pred)</th>
                  <th className="px-6 py-4">Attendance</th>
                  <th className="px-6 py-4">Risk Status</th>
                  <th className="px-6 py-4">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm dark:divide-slate-800">
                {filtered.map((st) => (
                  <tr
                    key={st.student_id}
                    className="transition hover:bg-slate-50/70 dark:hover:bg-slate-800/40"
                  >
                    <td className="px-6 py-4">
                      <p className="font-bold text-slate-900 dark:text-white">{st.full_name}</p>
                      <p className="text-xs text-slate-500">{st.email}</p>
                      {st.wants_mentor_talk && (
                        <span className="mt-1 inline-block rounded-full bg-rose-100 px-2 py-0.5 text-xs font-bold text-rose-700">
                          Requested Mentor Chat
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-semibold">{st.education_stage}</span> • {st.stream}
                    </td>
                    <td className="px-6 py-4 font-semibold">
                      {st.current_cgpa.toFixed(1)}{' '}
                      <span className="text-xs text-[#4F46E5]">({st.predicted_cgpa.toFixed(2)})</span>
                    </td>
                    <td className="px-6 py-4 font-semibold">{st.attendance_pct.toFixed(0)}%</td>
                    <td className="px-6 py-4">
                      <RiskBadge risk={st.risk_level} />
                    </td>
                    <td className="px-6 py-4">
                      <button
                        type="button"
                        onClick={() => openDrawer(st)}
                        className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-50 px-3.5 py-2 text-sm font-semibold text-[#4F46E5] hover:bg-indigo-100 dark:bg-indigo-950 dark:text-indigo-300"
                      >
                        <Eye className="h-4 w-4" aria-hidden="true" />
                        <span>View Details</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          {/* Student Detail Drawer */}
          {selected && (
            <div className="fixed inset-0 z-50 flex justify-end bg-slate-900/50 backdrop-blur-xs">
              <div className="h-full w-full max-w-lg overflow-y-auto bg-white p-6 shadow-2xl dark:bg-slate-900">
                <div className="flex items-start justify-between border-b border-slate-200 pb-4 dark:border-slate-800">
                  <div>
                    <h2 className="font-['Poppins'] text-xl font-bold">{selected.full_name}</h2>
                    <p className="text-sm text-slate-500">
                      {selected.education_stage} Pass-Out • {selected.stream}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setSelected(null)}
                    className="inline-flex items-center gap-1 rounded-xl border border-slate-200 px-3 py-1.5 text-sm font-semibold dark:border-slate-700"
                  >
                    <X className="h-4 w-4" aria-hidden="true" />
                    <span>Close</span>
                  </button>
                </div>

                <div className="mt-5 space-y-5">
                  <div className="flex items-center justify-between rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/60">
                    <div>
                      <p className="text-xs font-semibold text-slate-500">Predicted CGPA</p>
                      <p className="font-['Poppins'] text-2xl font-bold">
                        {selected.predicted_cgpa.toFixed(2)} / 10
                      </p>
                      <p className="text-xs text-slate-500">
                        Attendance: {selected.attendance_pct}% • Mood: {selected.latest_mood}
                      </p>
                    </div>
                    <RiskBadge risk={selected.risk_level} />
                  </div>

                  {/* AI Summary */}
                  <div>
                    <h3 className="text-sm font-bold uppercase tracking-wide text-slate-500">
                      AI Risk Summary
                    </h3>
                    <ul className="mt-2 space-y-2">
                      {selected.top_reasons.slice(0, 3).map((r) => (
                        <li
                          key={r.key}
                          className="rounded-xl border border-slate-200 p-3 text-sm dark:border-slate-800"
                        >
                          <span className="font-bold">{r.factor}: </span>
                          {r.plain_text}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Subject Marks */}
                  <div>
                    <h3 className="text-sm font-bold uppercase tracking-wide text-slate-500">
                      Subject Marks
                    </h3>
                    <div className="mt-2 grid grid-cols-2 gap-2">
                      {selected.subjects.map((sub) => (
                        <div
                          key={sub.name}
                          className="rounded-xl bg-slate-50 p-3 text-sm dark:bg-slate-800/70"
                        >
                          <p className="font-semibold">{sub.name}</p>
                          <p className="text-xs text-slate-500">
                            Internal: {sub.internal}% • Exam: {sub.exam}%
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Remarks & Meeting */}
                  <div className="space-y-3 border-t border-slate-200 pt-4 dark:border-slate-800">
                    <label className="block">
                      <span className="text-sm font-bold">Mentor Remarks / Notes</span>
                      <textarea
                        rows={3}
                        value={remarks}
                        onChange={(e) => setRemarks(e.target.value)}
                        placeholder="Add actionable guidance for this student..."
                        className="mt-1.5 w-full rounded-xl border border-slate-200 p-3 text-sm dark:border-slate-700 dark:bg-slate-800"
                      />
                    </label>

                    <label className="block">
                      <span className="text-sm font-bold">Meeting Date &amp; Time</span>
                      <input
                        type="text"
                        value={meetingAt}
                        onChange={(e) => setMeetingAt(e.target.value)}
                        placeholder="e.g. Friday, 28 Nov at 4:30 PM"
                        className="mt-1.5 w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-800"
                      />
                    </label>

                    {toast && (
                      <p className="rounded-xl bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-700">
                        {toast}
                      </p>
                    )}

                    <div className="flex flex-col gap-2.5 sm:flex-row">
                      <button
                        type="button"
                        disabled={saving}
                        onClick={() => saveMentorAction(false)}
                        className="inline-flex flex-1 items-center justify-center gap-2 rounded-xl bg-[#4F46E5] px-4 py-2.5 text-sm font-semibold text-white hover:bg-[#4338CA]"
                      >
                        <MessageSquarePlus className="h-4 w-4" aria-hidden="true" />
                        <span>Save Remark</span>
                      </button>
                      <button
                        type="button"
                        disabled={saving}
                        onClick={() => saveMentorAction(true)}
                        className="inline-flex flex-1 items-center justify-center gap-2 rounded-xl bg-[#14B8A6] px-4 py-2.5 text-sm font-semibold text-white hover:bg-[#0D9488]"
                      >
                        <CalendarPlus className="h-4 w-4" aria-hidden="true" />
                        <span>Schedule meeting</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </AppShell>
  )
}
