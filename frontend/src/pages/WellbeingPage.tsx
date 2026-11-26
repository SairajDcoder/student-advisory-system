import React, { useEffect, useState } from 'react'
import { HeartHandshake, MessageCircleHeart, Sparkles } from 'lucide-react'
import { AppShell } from '../components/AppShell'
import { Card } from '../components/ui'
import { apiRequest } from '../lib/api'
import { CheckinItem } from '../types'

const MOODS = [
  { id: 'happy', emoji: '😄', label: 'Happy' },
  { id: 'calm', emoji: '😌', label: 'Calm' },
  { id: 'okay', emoji: '🙂', label: 'Okay' },
  { id: 'stressed', emoji: '😟', label: 'Stressed' },
  { id: 'overwhelmed', emoji: '😫', label: 'Overwhelmed' },
]

export function WellbeingPage() {
  const [mood, setMood] = useState('calm')
  const [stress, setStress] = useState(2)
  const [sleep, setSleep] = useState(7.5)
  const [q1Focus, setQ1Focus] = useState('Mostly focused')
  const [q2Workload, setQ2Workload] = useState('Manageable')
  const [q3Breaks, setQ3Breaks] = useState('Yes, took short breaks')
  const [wantsMentor, setWantsMentor] = useState(false)
  const [history, setHistory] = useState<CheckinItem[]>([])
  const [latestSupport, setLatestSupport] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    apiRequest<CheckinItem[]>('/api/student/wellbeing').then(setHistory).catch(() => {})
  }, [])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    try {
      const res = await apiRequest<CheckinItem>('/api/student/wellbeing', {
        method: 'POST',
        body: JSON.stringify({
          mood,
          stress_score: stress,
          sleep_hours: sleep,
          answers: { focus: q1Focus, workload: q2Workload, breaks: q3Breaks },
          wants_mentor_talk: wantsMentor,
        }),
      })
      setLatestSupport(res.supportive_message)
      setHistory((prev) => [res, ...prev])
    } finally {
      setSaving(false)
    }
  }

  return (
    <AppShell>
      <div className="mx-auto max-w-3xl space-y-6">
        <div>
          <h1 className="font-['Poppins'] text-2xl font-bold">Wellbeing Check-in</h1>
          <p className="mt-1 text-base text-slate-600 dark:text-slate-300">
            A quick 30-second check on how you feel — your wellbeing matters just as much as marks.
          </p>
        </div>

        <Card>
          <form onSubmit={submit} className="space-y-6">
            {/* Emoji Mood Selector */}
            <div>
              <p className="text-base font-bold">1. How are you feeling today?</p>
              <div className="mt-3 grid grid-cols-3 gap-2.5 sm:grid-cols-5">
                {MOODS.map((m) => (
                  <button
                    key={m.id}
                    type="button"
                    onClick={() => setMood(m.id)}
                    className={`flex flex-col items-center gap-1 rounded-2xl border p-3 transition ${
                      mood === m.id
                        ? 'border-[#4F46E5] bg-indigo-50 ring-2 ring-[#4F46E5] dark:bg-indigo-950/60'
                        : 'border-slate-200 hover:bg-slate-50 dark:border-slate-700'
                    }`}
                  >
                    <span className="text-3xl" aria-hidden="true">
                      {m.emoji}
                    </span>
                    <span className="text-sm font-semibold">{m.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* 5 Quick Questions */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <label className="block">
                <span className="text-sm font-semibold">
                  2. Study stress right now ({stress} / 5)
                </span>
                <input
                  type="range"
                  min={1}
                  max={5}
                  value={stress}
                  onChange={(e) => setStress(Number(e.target.value))}
                  className="mt-2.5 w-full accent-[#4F46E5]"
                />
              </label>

              <label className="block">
                <span className="text-sm font-semibold">
                  3. Hours slept last night ({sleep} hrs)
                </span>
                <input
                  type="range"
                  min={3}
                  max={11}
                  step={0.5}
                  value={sleep}
                  onChange={(e) => setSleep(Number(e.target.value))}
                  className="mt-2.5 w-full accent-[#14B8A6]"
                />
              </label>

              <label className="block">
                <span className="text-sm font-semibold">4. How was your focus today?</span>
                <select
                  value={q1Focus}
                  onChange={(e) => setQ1Focus(e.target.value)}
                  className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-800"
                >
                  <option>Mostly focused</option>
                  <option>A bit distracted</option>
                  <option>Hard to concentrate</option>
                </select>
              </label>

              <label className="block">
                <span className="text-sm font-semibold">5. Does your workload feel okay?</span>
                <select
                  value={q2Workload}
                  onChange={(e) => setQ2Workload(e.target.value)}
                  className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-800"
                >
                  <option>Manageable</option>
                  <option>Slightly heavy</option>
                  <option>Too much right now</option>
                </select>
              </label>
            </div>

            <label className="flex items-center gap-3 rounded-xl border border-teal-200 bg-teal-50/70 p-4 dark:border-teal-900 dark:bg-teal-950/30">
              <input
                type="checkbox"
                checked={wantsMentor}
                onChange={(e) => setWantsMentor(e.target.checked)}
                className="h-5 w-5 rounded accent-[#14B8A6]"
              />
              <div>
                <p className="text-base font-semibold">Talk to a Mentor</p>
                <p className="text-sm text-slate-600 dark:text-slate-300">
                  Notify your faculty mentor to schedule a friendly, confidential 1-on-1 chat.
                </p>
              </div>
            </label>

            <button
              type="submit"
              disabled={saving}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-[#14B8A6] py-3.5 text-base font-bold text-white hover:bg-[#0D9488] disabled:opacity-60"
            >
              <HeartHandshake className="h-5 w-5" aria-hidden="true" />
              <span>{saving ? 'Saving check-in...' : 'Save Check-in & Get Support'}</span>
            </button>
          </form>
        </Card>

        {latestSupport && (
          <Card className="border-indigo-200 bg-indigo-50/70 dark:border-indigo-900 dark:bg-indigo-950/40">
            <div className="flex items-start gap-3">
              <Sparkles className="mt-0.5 h-6 w-6 shrink-0 text-[#4F46E5]" aria-hidden="true" />
              <div>
                <h2 className="font-['Poppins'] text-lg font-bold">A note for you</h2>
                <p className="mt-1 text-base leading-relaxed text-slate-700 dark:text-slate-200">
                  {latestSupport}
                </p>
              </div>
            </div>
          </Card>
        )}

        {history.length > 0 && (
          <Card>
            <h2 className="flex items-center gap-2 font-['Poppins'] text-lg font-bold">
              <MessageCircleHeart className="h-5 w-5 text-[#14B8A6]" aria-hidden="true" />
              <span>Recent Check-ins</span>
            </h2>
            <ul className="mt-3 space-y-2.5">
              {history.slice(0, 4).map((h) => (
                <li
                  key={h.id}
                  className="flex flex-col justify-between gap-1 rounded-xl bg-slate-50 p-3.5 text-sm sm:flex-row sm:items-center dark:bg-slate-800/70"
                >
                  <div>
                    <span className="font-bold capitalize">{h.mood}</span> • Stress {h.stress_score}/5 •{' '}
                    {h.sleep_hours} hrs sleep
                  </div>
                  {h.wants_mentor_talk && (
                    <span className="rounded-full bg-teal-100 px-2.5 py-0.5 text-xs font-bold text-teal-800">
                      Mentor notified
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </Card>
        )}
      </div>
    </AppShell>
  )
}
