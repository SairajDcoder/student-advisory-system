import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { GraduationCap, LogIn, ShieldCheck, UserPlus, Users } from 'lucide-react'
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
      setError('Supabase environment variables are missing. Check frontend/.env.')
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
          setError('Signed in with Supabase, but could not reach the AdvisorAI backend API.')
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
          setInfo('Account created! Please check your email inbox to confirm, then sign in.')
          setMode('login')
        }
      }
    } catch {
      setError('Unable to reach authentication service. Please try again.')
    } finally {
      setBusy(false)
    }
  }

  const handleOAuth = async (provider: 'google' | 'github') => {
    setError('')
    setInfo('')
    if (!isSupabaseConfigured) {
      setError('Supabase environment variables are missing. Check frontend/.env.')
      return
    }
    setBusy(true)
    try {
      const { error: oauthErr } = await supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: window.location.origin,
        },
      })
      if (oauthErr) {
        setError(oauthErr.message)
      }
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#F8FAFC] p-4 dark:bg-slate-950">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-7 shadow-lg sm:p-8 dark:border-slate-800 dark:bg-slate-900">
        <div className="text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-[#4F46E5] text-white shadow-sm">
            <GraduationCap className="h-7 w-7" aria-hidden="true" />
          </div>
          <h1 className="mt-4 font-['Poppins'] text-2xl font-bold text-slate-900 dark:text-white">
            AdvisorAI
          </h1>
          <p className="mt-1 text-base text-slate-600 dark:text-slate-300">
            Smart guidance for 10th &amp; 12th graduates
          </p>
        </div>

        {/* Mode Switch */}
        <div className="mt-6 grid grid-cols-2 rounded-xl bg-slate-100 p-1 dark:bg-slate-800">
          <button
            type="button"
            onClick={() => {
              setMode('login')
              setError('')
              setInfo('')
            }}
            className={`rounded-lg py-2 text-sm font-semibold transition ${
              mode === 'login'
                ? 'bg-white text-slate-900 shadow-sm dark:bg-slate-700 dark:text-white'
                : 'text-slate-600 dark:text-slate-400'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => {
              setMode('register')
              setError('')
              setInfo('')
            }}
            className={`rounded-lg py-2 text-sm font-semibold transition ${
              mode === 'register'
                ? 'bg-white text-slate-900 shadow-sm dark:bg-slate-700 dark:text-white'
                : 'text-slate-600 dark:text-slate-400'
            }`}
          >
            Create Account
          </button>
        </div>

        {/* Role Selector (for Registration) */}
        {mode === 'register' && (
          <div className="mt-5">
            <p className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-300">
              Select your role
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
                    className={`flex flex-col items-center gap-1 rounded-xl border py-2.5 text-sm font-semibold transition ${
                      active
                        ? 'border-[#4F46E5] bg-indigo-50 text-[#4F46E5] dark:bg-indigo-950/60 dark:text-indigo-300'
                        : 'border-slate-200 text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300'
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
            className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-800 dark:border-rose-900 dark:bg-rose-950/50 dark:text-rose-200"
          >
            {error}
          </div>
        )}

        {info && (
          <div className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950/50 dark:text-emerald-200">
            {info}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          {mode === 'register' && (
            <>
              <label className="block">
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                  Full Name
                </span>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Enter your full name"
                  className="mt-1 w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-base dark:border-slate-700 dark:bg-slate-800"
                />
              </label>

              {role === 'student' && (
                <div className="grid grid-cols-2 gap-3">
                  <label className="block">
                    <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                      Completed
                    </span>
                    <select
                      value={educationStage}
                      onChange={(e) => setEducationStage(e.target.value as '10th' | '12th')}
                      className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-800"
                    >
                      <option value="10th">10th Pass-Out</option>
                      <option value="12th">12th Pass-Out</option>
                    </select>
                  </label>
                  <label className="block">
                    <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                      Stream
                    </span>
                    <select
                      value={stream}
                      onChange={(e) => setStream(e.target.value)}
                      className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-800"
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
            <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
              Email Address
            </span>
            <input
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="mt-1 w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-base dark:border-slate-700 dark:bg-slate-800"
            />
          </label>

          <label className="block">
            <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
              Password
            </span>
            <input
              type="password"
              required
              minLength={6}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Minimum 6 characters"
              className="mt-1 w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-base dark:border-slate-700 dark:bg-slate-800"
            />
          </label>

          <button
            type="submit"
            disabled={busy}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-[#4F46E5] py-3 text-base font-semibold text-white shadow-sm hover:bg-[#4338CA] disabled:opacity-60"
          >
            {mode === 'login' ? (
              <>
                <LogIn className="h-5 w-5" aria-hidden="true" />
                <span>{busy ? 'Signing in...' : 'Sign In'}</span>
              </>
            ) : (
              <>
                <UserPlus className="h-5 w-5" aria-hidden="true" />
                <span>{busy ? 'Creating account...' : 'Create Account'}</span>
              </>
            )}
          </button>
        </form>

        <div className="my-4 flex items-center gap-3">
          <div className="h-px flex-1 bg-slate-200 dark:bg-slate-800" />
          <span className="text-xs font-medium text-slate-400">OR CONTINUE WITH</span>
          <div className="h-px flex-1 bg-slate-200 dark:bg-slate-800" />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => handleOAuth('google')}
            disabled={busy}
            className="flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
          >
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-slate-100 text-xs font-bold text-[#4F46E5]">
              G
            </span>
            <span>Google</span>
          </button>

          <button
            type="button"
            onClick={() => handleOAuth('github')}
            disabled={busy}
            className="flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
          >
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-slate-900 text-xs font-bold text-white">
              GH
            </span>
            <span>GitHub</span>
          </button>
        </div>

        <p className="mt-4 text-center text-xs text-slate-500 dark:text-slate-400">
          Secured by Supabase Authentication
        </p>
      </div>
    </div>
  )
}
