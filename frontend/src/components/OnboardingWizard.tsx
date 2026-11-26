import React, { useState } from 'react'
import { ArrowRight, CheckCircle2, Sparkles } from 'lucide-react'
import { apiRequest } from '../lib/api'
import { useAuth } from '../context/AuthContext'

const INTEREST_OPTIONS = [
  'Artificial Intelligence',
  'Data Science',
  'Web Development',
  'UI/UX Design',
  'Finance & Business',
  'Biotechnology & Health',
  'Coding & Apps',
  'Law & Civil Services',
]

export function OnboardingWizard({ onComplete }: { onComplete: () => void }) {
  const { refreshUser } = useAuth()
  const [step, setStep] = useState(1)
  const [educationStage, setEducationStage] = useState<'10th' | '12th'>('12th')
  const [boardName, setBoardName] = useState('CBSE')
  const [stream, setStream] = useState('Science (PCM)')
  const [boardPct, setBoardPct] = useState(80)
  const [attendancePct, setAttendancePct] = useState(82)
  const [internalMarks, setInternalMarks] = useState(76)
  const [assignmentScore, setAssignmentScore] = useState(78)
  const [studyHours, setStudyHours] = useState(18)
  const [interests, setInterests] = useState<string[]>([])
  const [skills, setSkills] = useState({
    Python: 60,
    'Analytical Thinking': 70,
    Communication: 70,
    Design: 55,
  })
  const [goals, setGoals] = useState('')
  const [saving, setSaving] = useState(false)

  const toggleInterest = (topic: string) => {
    setInterests((prev) =>
      prev.includes(topic) ? prev.filter((t) => t !== topic) : [...prev, topic]
    )
  }

  const handleFinish = async (skip = false) => {
    setSaving(true)
    try {
      await apiRequest('/api/student/onboarding', {
        method: 'POST',
        body: JSON.stringify({
          education_stage: educationStage,
          board_name: boardName,
          stream,
          board_percentage: boardPct,
          attendance_pct: attendancePct,
          internal_marks_avg: internalMarks,
          assignment_score_avg: assignmentScore,
          study_hours_per_week: studyHours,
          interests,
          skills,
          goals: goals || 'Build strong skills and choose the best career path.',
          skip,
        }),
      })
      await refreshUser()
      onComplete()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/65 p-4 backdrop-blur-sm">
      <div className="max-h-[92vh] w-full max-w-2xl overflow-y-auto rounded-2xl bg-white p-6 shadow-2xl sm:p-8 dark:bg-slate-900">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-[#7B2D8E] dark:text-purple-300">
            <Sparkles className="h-5 w-5" aria-hidden="true" />
            <span className="text-sm font-bold">Quick Setup • Step {step} of 3</span>
          </div>
          <button
            type="button"
            onClick={() => handleFinish(true)}
            disabled={saving}
            className="text-sm font-semibold text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200"
          >
            Skip for now
          </button>
        </div>

        <div className="mt-3 h-2.5 w-full overflow-hidden rounded-full bg-purple-100 dark:bg-slate-800">
          <div
            className="h-full rounded-full bg-gradient-to-r from-[#7B2D8E] to-[#FF6B4A] transition-all duration-300"
            style={{ width: `${(step / 3) * 100}%` }}
          />
        </div>

        {step === 1 && (
          <div className="mt-6 space-y-5">
            <div>
              <h2 className="font-['Poppins'] text-2xl font-bold">Your Academic Profile</h2>
              <p className="mt-1 text-base text-slate-600 dark:text-slate-300">
                Tell us your 10th or 12th scores and study routine so your roadmap matches you.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {(['10th', '12th'] as const).map((st) => (
                <button
                  key={st}
                  type="button"
                  onClick={() => setEducationStage(st)}
                  className={`rounded-2xl border p-4 text-left transition ${
                    educationStage === st
                      ? 'border-[#7B2D8E] bg-purple-50/70 ring-2 ring-[#7B2D8E] dark:bg-purple-950/50'
                      : 'border-slate-200 hover:border-slate-300 dark:border-slate-700'
                  }`}
                >
                  <p className="text-base font-bold">Just Completed {st}</p>
                  <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                    {st === '10th'
                      ? 'Get Class 11–12 stream & long-term career matches.'
                      : 'Get degree, career role & skill-gap guidance.'}
                  </p>
                </button>
              ))}
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <label className="block">
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                  Board
                </span>
                <select
                  value={boardName}
                  onChange={(e) => setBoardName(e.target.value)}
                  className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-base dark:border-slate-700 dark:bg-slate-800"
                >
                  <option>CBSE</option>
                  <option>ICSE</option>
                  <option>State Board</option>
                </select>
              </label>

              <label className="block">
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                  Stream / Track
                </span>
                <select
                  value={stream}
                  onChange={(e) => setStream(e.target.value)}
                  className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-base dark:border-slate-700 dark:bg-slate-800"
                >
                  <option>General</option>
                  <option>Science (PCM)</option>
                  <option>Science (PCB)</option>
                  <option>Commerce</option>
                  <option>Arts</option>
                </select>
              </label>

              <label className="block">
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                  Board Percentage ({boardPct}%)
                </span>
                <input
                  type="range"
                  min={35}
                  max={99}
                  value={boardPct}
                  onChange={(e) => setBoardPct(Number(e.target.value))}
                  className="mt-2.5 w-full accent-[#7B2D8E]"
                />
              </label>

              <label className="block">
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                  Attendance ({attendancePct}%)
                </span>
                <input
                  type="range"
                  min={35}
                  max={100}
                  value={attendancePct}
                  onChange={(e) => setAttendancePct(Number(e.target.value))}
                  className="mt-2.5 w-full accent-[#14B8A6]"
                />
              </label>

              <label className="block">
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                  Internal / Pre-Board Marks ({internalMarks}%)
                </span>
                <input
                  type="range"
                  min={30}
                  max={100}
                  value={internalMarks}
                  onChange={(e) => setInternalMarks(Number(e.target.value))}
                  className="mt-2.5 w-full accent-[#7B2D8E]"
                />
              </label>

              <label className="block">
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                  Weekly Study Hours ({studyHours} hrs)
                </span>
                <input
                  type="range"
                  min={2}
                  max={45}
                  value={studyHours}
                  onChange={(e) => setStudyHours(Number(e.target.value))}
                  className="mt-2.5 w-full accent-[#FF6B4A]"
                />
              </label>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="mt-6 space-y-5">
            <div>
              <h2 className="font-['Poppins'] text-2xl font-bold">Your Interests &amp; Skills</h2>
              <p className="mt-1 text-base text-slate-600 dark:text-slate-300">
                Pick what excites you and slide your comfort level.
              </p>
            </div>

            <div className="flex flex-wrap gap-2.5">
              {INTEREST_OPTIONS.map((topic) => {
                const active = interests.includes(topic)
                return (
                  <button
                    key={topic}
                    type="button"
                    onClick={() => toggleInterest(topic)}
                    className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                      active
                        ? 'bg-[#7B2D8E] text-white'
                        : 'border border-slate-200 bg-slate-50 text-slate-700 hover:bg-purple-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200'
                    }`}
                  >
                    {topic}
                  </button>
                )
              })}
            </div>

            <div className="space-y-3 pt-2">
              {Object.entries(skills).map(([name, val]) => (
                <div key={name}>
                  <div className="flex justify-between text-sm font-semibold">
                    <span>{name}</span>
                    <span className="text-[#7B2D8E]">{val}%</span>
                  </div>
                  <input
                    type="range"
                    min={20}
                    max={95}
                    value={val}
                    onChange={(e) =>
                      setSkills((prev) => ({ ...prev, [name]: Number(e.target.value) }))
                    }
                    className="mt-1 w-full accent-[#7B2D8E]"
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="mt-6 space-y-5">
            <div>
              <h2 className="font-['Poppins'] text-2xl font-bold">Your Main Goal</h2>
              <p className="mt-1 text-base text-slate-600 dark:text-slate-300">
                What do you want to achieve in the next 6–12 months?
              </p>
            </div>

            <textarea
              rows={4}
              value={goals}
              onChange={(e) => setGoals(e.target.value)}
              placeholder="e.g. Pick the right college degree after 12th, improve Maths score, and build Python projects."
              className="w-full rounded-2xl border border-slate-200 bg-[#FAF7FD] p-4 text-base focus:border-[#7B2D8E] focus:bg-white focus:outline-none dark:border-slate-700 dark:bg-slate-800"
            />
          </div>
        )}

        <div className="mt-8 flex items-center justify-between gap-4">
          {step > 1 ? (
            <button
              type="button"
              onClick={() => setStep((s) => s - 1)}
              className="rounded-xl border border-slate-200 px-5 py-3 text-base font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200"
            >
              Back
            </button>
          ) : (
            <div />
          )}

          {step < 3 ? (
            <button
              type="button"
              onClick={() => setStep((s) => s + 1)}
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-[#FF7A45] to-[#FF5163] px-6 py-3 text-base font-bold text-white shadow-sm hover:brightness-105"
            >
              <span>Continue</span>
              <ArrowRight className="h-5 w-5" aria-hidden="true" />
            </button>
          ) : (
            <button
              type="button"
              onClick={() => handleFinish(false)}
              disabled={saving}
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-[#FF7A45] to-[#FF5163] px-6 py-3 text-base font-bold text-white shadow-sm hover:brightness-105 disabled:opacity-60"
            >
              <CheckCircle2 className="h-5 w-5" aria-hidden="true" />
              <span>{saving ? 'Saving...' : 'Launch My Dashboard'}</span>
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
