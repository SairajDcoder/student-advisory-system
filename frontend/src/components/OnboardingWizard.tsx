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
  const [boardPct, setBoardPct] = useState(82)
  const [studyHours, setStudyHours] = useState(20)
  const [interests, setInterests] = useState<string[]>(['Artificial Intelligence', 'Coding & Apps'])
  const [skills, setSkills] = useState({
    Python: 65,
    'Analytical Thinking': 75,
    Communication: 70,
    Design: 60,
  })
  const [goals, setGoals] = useState(
    'Pick the best career track after board exams and keep my grades stress-free.'
  )
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
          study_hours_per_week: studyHours,
          interests,
          skills,
          goals,
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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4 backdrop-blur-sm">
      <div className="w-full max-w-2xl rounded-2xl bg-white p-6 shadow-2xl sm:p-8 dark:bg-slate-900">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-[#4F46E5] dark:text-indigo-400">
            <Sparkles className="h-5 w-5" aria-hidden="true" />
            <span className="text-sm font-semibold">Welcome Setup • Step {step} of 3</span>
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

        {/* Progress Bar */}
        <div className="mt-3 h-2.5 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
          <div
            className="h-full rounded-full bg-[#4F46E5] transition-all duration-300"
            style={{ width: `${(step / 3) * 100}%` }}
          />
        </div>

        {step === 1 && (
          <div className="mt-6 space-y-5">
            <div>
              <h2 className="font-['Poppins'] text-2xl font-bold">Tell us your current stage</h2>
              <p className="mt-1 text-base text-slate-600 dark:text-slate-300">
                We tailor stream, degree, and career advice specifically for 10th &amp; 12th graduates.
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
                      ? 'border-[#4F46E5] bg-indigo-50/70 ring-2 ring-[#4F46E5] dark:bg-indigo-950/50'
                      : 'border-slate-200 hover:border-slate-300 dark:border-slate-700'
                  }`}
                >
                  <p className="text-base font-bold">Just Completed {st}</p>
                  <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                    {st === '10th'
                      ? 'Get 11th–12th stream & long-term career suggestions.'
                      : 'Get degree, role & skill-gap recommendations.'}
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
                  Latest Board % ({boardPct}%)
                </span>
                <input
                  type="range"
                  min={40}
                  max={99}
                  value={boardPct}
                  onChange={(e) => setBoardPct(Number(e.target.value))}
                  className="mt-3 w-full accent-[#4F46E5]"
                />
              </label>

              <label className="block">
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                  Weekly Study Hours ({studyHours} hrs)
                </span>
                <input
                  type="range"
                  min={4}
                  max={45}
                  value={studyHours}
                  onChange={(e) => setStudyHours(Number(e.target.value))}
                  className="mt-3 w-full accent-[#14B8A6]"
                />
              </label>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="mt-6 space-y-5">
            <div>
              <h2 className="font-['Poppins'] text-2xl font-bold">Your interests &amp; comfort</h2>
              <p className="mt-1 text-base text-slate-600 dark:text-slate-300">
                Pick topics you enjoy — this helps AdvisorAI match real-world careers.
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
                        ? 'bg-[#4F46E5] text-white'
                        : 'border border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200'
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
                    <span className="text-[#4F46E5]">{val}%</span>
                  </div>
                  <input
                    type="range"
                    min={20}
                    max={95}
                    value={val}
                    onChange={(e) =>
                      setSkills((prev) => ({ ...prev, [name]: Number(e.target.value) }))
                    }
                    className="mt-1 w-full accent-[#4F46E5]"
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="mt-6 space-y-5">
            <div>
              <h2 className="font-['Poppins'] text-2xl font-bold">What is your main goal?</h2>
              <p className="mt-1 text-base text-slate-600 dark:text-slate-300">
                Write in plain words — e.g. &ldquo;Crack CS degree, keep 8.5+ CGPA, reduce exam stress.&rdquo;
              </p>
            </div>

            <textarea
              rows={4}
              value={goals}
              onChange={(e) => setGoals(e.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 p-4 text-base focus:border-[#4F46E5] focus:bg-white focus:outline-none dark:border-slate-700 dark:bg-slate-800"
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
              className="inline-flex items-center gap-2 rounded-xl bg-[#4F46E5] px-6 py-3 text-base font-semibold text-white hover:bg-[#4338CA]"
            >
              <span>Continue</span>
              <ArrowRight className="h-5 w-5" aria-hidden="true" />
            </button>
          ) : (
            <button
              type="button"
              onClick={() => handleFinish(false)}
              disabled={saving}
              className="inline-flex items-center gap-2 rounded-xl bg-[#14B8A6] px-6 py-3 text-base font-semibold text-white hover:bg-[#0D9488] disabled:opacity-60"
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
