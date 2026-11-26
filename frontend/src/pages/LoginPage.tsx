import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowRight,
  Award,
  BarChart3,
  BookOpen,
  Check,
  Compass,
  GraduationCap,
  ShieldCheck,
  Sparkles,
  Users,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { isSupabaseConfigured, supabase } from '../lib/supabase'
import { Role } from '../types'

export function LoginPage() {
  const { refreshUser } = useAuth()
  const navigate = useNavigate()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [role, setRole] = useState<Role>('student')
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [educationStage, setEducationStage] = useState<'10th' | '12th'>('12th')
  const [stream, setStream] = useState('Science (PCM)')
  const [error, setError] = useState('')
  const [info, setInfo] = useState('')
  const [busy, setBusy] = useState(false)

  const routeForRole = (r: Role) => {
    if (r === 'mentor') return '/mentor'
    if (r === 'admin') return '/admin'
    return '/'
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setInfo('')

    if (!isSupabaseConfigured) {
      setError('Supabase environment variables are missing. Please check frontend/.env.')
      return
    }

    setBusy(true)
    try {
      if (mode === 'login') {
        const { error: authErr } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password,
        })
        if (authErr) {
          setError(authErr.message)
          return
        }
        const me = await refreshUser()
        if (me) {
          navigate(routeForRole(me.role))
        } else {
          setError('Signed in, but the AdvisorAI server is currently unreachable. Start the FastAPI backend and try again.')
        }
      } else {
        const { data, error: signUpErr } = await supabase.auth.signUp({
          email: email.trim(),
          password,
          options: {
            data: {
              full_name: fullName.trim(),
              role,
              education_stage: educationStage,
              stream,
              department: `${educationStage} Pass-Out (${stream})`,
            },
          },
        })
        if (signUpErr) {
          setError(signUpErr.message)
          return
        }
        if (data.session) {
          const me = await refreshUser()
          navigate(routeForRole(me?.role || role))
        } else {
          setInfo('Your account is ready! Please confirm your email if prompted, then sign in.')
          setMode('login')
        }
      }
    } catch {
      setError('Unable to reach authentication service. Please try again.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-[#883898] via-[#6F2784] to-[#4A175D] text-white">
      {/* Subtle Decorative Curves & Floating Academic Badges (BYJU'S-inspired) */}
      <div className="pointer-events-none absolute -left-24 -top-24 h-96 w-96 rounded-full bg-white/5 blur-2xl" />
      <div className="pointer-events-none absolute -bottom-32 right-1/3 h-96 w-96 rounded-full bg-[#FF7A45]/15 blur-3xl" />

      {/* Top Navigation Brand Strip */}
      <header className="relative z-10 mx-auto flex max-w-7xl items-center justify-between px-5 py-5 sm:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white text-[#7B2D8E] shadow-md">
            <GraduationCap className="h-6 w-6" aria-hidden="true" />
          </div>
          <div>
            <span className="block font-['Poppins'] text-xl font-bold tracking-tight text-white">
              AdvisorAI
            </span>
            <span className="block text-xs font-medium text-purple-200">
              For Class 10th &amp; 12th Students
            </span>
          </div>
        </div>

        <div className="hidden items-center gap-6 text-sm font-medium text-purple-100 md:flex">
          <span className="inline-flex items-center gap-1.5">
            <Compass className="h-4 w-4 text-[#FFB347]" aria-hidden="true" />
            Stream &amp; Career Finder
          </span>
          <span className="inline-flex items-center gap-1.5">
            <BarChart3 className="h-4 w-4 text-[#14B8A6]" aria-hidden="true" />
            Smart CGPA Forecast
          </span>
          <span className="inline-flex items-center gap-1.5">
            <BookOpen className="h-4 w-4 text-[#FF7A45]" aria-hidden="true" />
            Weekly Study Planner
          </span>
        </div>
      </header>

      {/* Main Split Hero Container */}
      <main className="relative z-10 mx-auto grid max-w-7xl grid-cols-1 items-center gap-10 px-5 pb-12 pt-4 sm:px-8 lg:grid-cols-12 lg:py-10">
        {/* Left Hero Column — Teenager-Friendly Showcase */}
        <section className="space-y-7 lg:col-span-7">
          <div className="inline-flex items-center gap-2 rounded-full bg-white/15 px-4 py-1.5 text-sm font-semibold text-amber-200 backdrop-blur-sm">
            <Sparkles className="h-4 w-4" aria-hidden="true" />
            <span>Built for 10th &amp; 12th Board Graduates</span>
          </div>

          <h1 className="font-['Poppins'] text-3xl font-bold leading-tight tracking-tight text-white sm:text-5xl">
            Finished 10th or 12th?{' '}
            <span className="text-[#FFD166]">Discover your best stream &amp; career path.</span>
          </h1>

          <p className="max-w-xl text-base leading-relaxed text-purple-100 sm:text-lg">
            No confusing charts or guesswork. Enter your marks and interests to see which streams,
            colleges, and skills fit you best — plus get a personal weekly study plan and mentor support.
          </p>

          {/* Interactive Visual Preview Collage (Inspired by BYJU'S Floating Concept Cards) */}
          <div className="relative grid max-w-xl grid-cols-2 gap-4 pt-2 sm:grid-cols-3">
            {/* Floating STEM / Subject Report Mini Card */}
            <div className="rounded-2xl bg-white p-4 text-slate-900 shadow-xl">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wide text-[#7B2D8E]">
                  Subject Score
                </span>
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-amber-400 text-xs font-extrabold text-slate-900">
                  f(x)
                </span>
              </div>
              <p className="mt-2 font-['Poppins'] text-2xl font-bold text-slate-900">
                95<span className="text-sm font-medium text-slate-400">/100</span>
              </p>
              <div className="mt-2 flex items-end gap-1.5">
                <div className="h-5 w-3 rounded-t bg-purple-200" />
                <div className="h-8 w-3 rounded-t bg-purple-400" />
                <div className="h-10 w-3 rounded-t bg-[#7B2D8E]" />
                <div className="h-7 w-3 rounded-t bg-[#14B8A6]" />
                <span className="ml-auto text-xs font-bold text-emerald-600">PCM Fit</span>
              </div>
            </div>

            {/* Career Match Preview Card */}
            <div className="rounded-2xl bg-white p-4 text-slate-900 shadow-xl">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wide text-[#0D9488]">
                  Top Match
                </span>
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-[#FF8C42] to-[#FF5163] text-xs font-extrabold text-white">
                  π
                </span>
              </div>
              <p className="mt-2 font-['Poppins'] text-base font-bold leading-snug text-slate-900">
                AI &amp; Data Science
              </p>
              <p className="mt-1 text-xs font-semibold text-emerald-600">92% Skill Match</p>
              <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-100">
                <div className="h-full w-[92%] rounded-full bg-gradient-to-r from-[#7B2D8E] to-[#14B8A6]" />
              </div>
            </div>

            {/* Student Streak / Mentor Card */}
            <div className="col-span-2 rounded-2xl bg-white/15 p-4 text-white backdrop-blur-md sm:col-span-1">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#FFD166] text-slate-900">
                <Award className="h-4 w-4" aria-hidden="true" />
              </div>
              <p className="mt-2.5 text-sm font-bold">1-on-1 Mentor &amp; AI Chat</p>
              <p className="mt-1 text-xs text-purple-100">
                Ask doubts anytime &amp; track your stress-free study plan.
              </p>
            </div>
          </div>

          <div className="flex flex-wrap gap-3 pt-1 text-xs font-semibold text-purple-100 sm:text-sm">
            <span className="rounded-full border border-white/25 bg-white/10 px-3.5 py-1.5">
              ✓ 10th Stream Selection (PCM / PCB / Commerce / Arts)
            </span>
            <span className="rounded-full border border-white/25 bg-white/10 px-3.5 py-1.5">
              ✓ 12th Degree &amp; Career Roadmap
            </span>
          </div>
        </section>

        {/* Right Column — Crisp White Card (BYJU'S Form Style) */}
        <section className="lg:col-span-5">
          <div className="mx-auto w-full max-w-md rounded-2xl bg-white p-6 text-slate-900 shadow-2xl sm:p-8">
            <div className="text-center">
              <h2 className="font-['Poppins'] text-2xl font-bold text-slate-900">
                {mode === 'login' ? 'Welcome Back!' : 'Join AdvisorAI Free'}
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                {mode === 'login'
                  ? 'Sign in to check your dashboard & career plan'
                  : 'Create your student, mentor, or admin account in 30 seconds'}
              </p>
            </div>

            {/* Mode Selector styled like BYJU'S Online/Offline selector */}
            <div className="mt-6">
              <p className="mb-2 text-center text-xs font-bold uppercase tracking-wider text-slate-500">
                Choose Account Action
              </p>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setMode('login')
                    setError('')
                    setInfo('')
                  }}
                  className={`relative rounded-xl border-2 py-2.5 text-sm font-bold transition ${
                    mode === 'login'
                      ? 'border-[#7B2D8E] bg-purple-50/50 text-[#7B2D8E]'
                      : 'border-slate-200 text-slate-600 hover:border-slate-300'
                  }`}
                >
                  {mode === 'login' && (
                    <span className="absolute -right-2 -top-2 flex h-5 w-5 items-center justify-center rounded-full bg-[#7B2D8E] text-white shadow">
                      <Check className="h-3 w-3" aria-hidden="true" />
                    </span>
                  )}
                  Sign In
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setMode('register')
                    setError('')
                    setInfo('')
                  }}
                  className={`relative rounded-xl border-2 py-2.5 text-sm font-bold transition ${
                    mode === 'register'
                      ? 'border-[#7B2D8E] bg-purple-50/50 text-[#7B2D8E]'
                      : 'border-slate-200 text-slate-600 hover:border-slate-300'
                  }`}
                >
                  {mode === 'register' && (
                    <span className="absolute -right-2 -top-2 flex h-5 w-5 items-center justify-center rounded-full bg-[#7B2D8E] text-white shadow">
                      <Check className="h-3 w-3" aria-hidden="true" />
                    </span>
                  )}
                  Create Account
                </button>
              </div>
            </div>

            {/* Role Selector on Registration */}
            {mode === 'register' && (
              <div className="mt-5">
                <p className="mb-2 text-xs font-bold uppercase tracking-wider text-slate-500">
                  I am a
                </p>
                <div className="grid grid-cols-3 gap-2">
                  {(
                    [
                      { id: 'student', label: 'Student', icon: GraduationCap },
                      { id: 'mentor', label: 'Mentor', icon: Users },
                      { id: 'admin', label: 'Admin', icon: ShieldCheck },
                    ] as const
                  ).map((r) => {
                    const Icon = r.icon
                    const active = role === r.id
                    return (
                      <button
                        key={r.id}
                        type="button"
                        onClick={() => setRole(r.id)}
                        className={`flex items-center justify-center gap-1.5 rounded-xl border py-2 text-xs font-bold transition ${
                          active
                            ? 'border-[#7B2D8E] bg-purple-50 text-[#7B2D8E]'
                            : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                        }`}
                      >
                        <Icon className="h-4 w-4" aria-hidden="true" />
                        <span>{r.label}</span>
                      </button>
                    )
                  })}
                </div>
              </div>
            )}

            {error && (
              <div
                role="alert"
                className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-800"
              >
                {error}
              </div>
            )}

            {info && (
              <div className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-800">
                {info}
              </div>
            )}

            <form onSubmit={handleSubmit} className="mt-5 space-y-3.5">
              {mode === 'register' && (
                <>
                  <label className="block">
                    <span className="text-xs font-bold uppercase tracking-wide text-slate-600">
                      Full Name <span className="text-rose-500">*</span>
                    </span>
                    <input
                      type="text"
                      required
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Enter your full name"
                      className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-base text-slate-900 placeholder:text-slate-400 focus:border-[#7B2D8E] focus:outline-none"
                    />
                  </label>

                  {role === 'student' && (
                    <div className="grid grid-cols-2 gap-3">
                      <label className="block">
                        <span className="text-xs font-bold uppercase tracking-wide text-slate-600">
                          Just Passed
                        </span>
                        <select
                          value={educationStage}
                          onChange={(e) => setEducationStage(e.target.value as '10th' | '12th')}
                          className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm font-medium text-slate-900 focus:border-[#7B2D8E] focus:outline-none"
                        >
                          <option value="10th">Class 10th</option>
                          <option value="12th">Class 12th</option>
                        </select>
                      </label>
                      <label className="block">
                        <span className="text-xs font-bold uppercase tracking-wide text-slate-600">
                          Stream
                        </span>
                        <select
                          value={stream}
                          onChange={(e) => setStream(e.target.value)}
                          className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm font-medium text-slate-900 focus:border-[#7B2D8E] focus:outline-none"
                        >
                          <option>Science (PCM)</option>
                          <option>Science (PCB)</option>
                          <option>Commerce</option>
                          <option>Arts</option>
                          <option>General</option>
                        </select>
                      </label>
                    </div>
                  )}
                </>
              )}

              <label className="block">
                <span className="text-xs font-bold uppercase tracking-wide text-slate-600">
                  Email Address <span className="text-rose-500">*</span>
                </span>
                <input
                  type="email"
                  required
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email address"
                  className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-base text-slate-900 placeholder:text-slate-400 focus:border-[#7B2D8E] focus:outline-none"
                />
              </label>

              <label className="block">
                <span className="text-xs font-bold uppercase tracking-wide text-slate-600">
                  Password <span className="text-rose-500">*</span>
                </span>
                <input
                  type="password"
                  required
                  minLength={6}
                  autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Minimum 6 characters"
                  className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-base text-slate-900 placeholder:text-slate-400 focus:border-[#7B2D8E] focus:outline-none"
                />
              </label>

              {/* Signature BYJU'S Coral-Orange Gradient CTA */}
              <button
                type="submit"
                disabled={busy}
                className="mt-2 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[#FF7A45] to-[#FF5163] py-3.5 text-base font-bold text-white shadow-md transition hover:brightness-105 disabled:opacity-60"
              >
                <span>
                  {busy
                    ? 'Please wait...'
                    : mode === 'login'
                    ? 'Continue to Dashboard'
                    : 'Start My Free Journey'}
                </span>
                <ArrowRight className="h-5 w-5" aria-hidden="true" />
              </button>
            </form>

            <p className="mt-5 text-center text-xs text-slate-400">
              {mode === 'login' ? (
                <>
                  New to AdvisorAI?{' '}
                  <button
                    type="button"
                    onClick={() => setMode('register')}
                    className="font-bold text-[#7B2D8E] hover:underline"
                  >
                    Create a free account
                  </button>
                </>
              ) : (
                <>
                  Already have an account?{' '}
                  <button
                    type="button"
                    onClick={() => setMode('login')}
                    className="font-bold text-[#7B2D8E] hover:underline"
                  >
                    Sign in here
                  </button>
                </>
              )}
            </p>
          </div>
        </section>
      </main>
    </div>
  )
}
