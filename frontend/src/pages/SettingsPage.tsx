import React, { useState } from 'react'
import { Save } from 'lucide-react'
import { AppShell } from '../components/AppShell'
import { Card } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import { apiRequest } from '../lib/api'

export function SettingsPage() {
  const { user, theme, setThemeMode, refreshUser } = useAuth()
  const [fullName, setFullName] = useState(user?.full_name || '')
  const [department, setDepartment] = useState(user?.department || '')
  const [educationStage, setEducationStage] = useState(user?.education_stage || '12th')
  const [stream, setStream] = useState(user?.stream || 'Science (PCM)')
  const [language, setLanguage] = useState(user?.language_preference || 'en')
  const [notificationsEnabled, setNotificationsEnabled] = useState(
    user?.notifications_enabled ?? true
  )
  const [saved, setSaved] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setSaved('')
    try {
      await apiRequest('/api/profile', {
        method: 'PATCH',
        body: JSON.stringify({
          full_name: fullName,
          department,
          education_stage: educationStage,
          stream,
          theme_preference: theme,
          language_preference: language,
          notifications_enabled: notificationsEnabled,
        }),
      })
      await refreshUser()
      setSaved('Your profile & preferences have been saved.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <AppShell>
      <div className="mx-auto max-w-2xl space-y-6">
        <div className="rounded-2xl bg-gradient-to-r from-[#7B2D8E] to-[#581C68] p-6 text-white shadow-md">
          <h1 className="font-['Poppins'] text-2xl font-bold">Profile &amp; Settings</h1>
          <p className="mt-1 text-base text-purple-100">
            Update your details, 10th/12th track, theme, language, and alert preferences.
          </p>
        </div>

        <Card>
          <form onSubmit={handleSave} className="space-y-5">
            <label className="block">
              <span className="text-sm font-semibold">Full Name</span>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="mt-1.5 w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-base dark:border-slate-700 dark:bg-slate-800"
              />
            </label>

            <label className="block">
              <span className="text-sm font-semibold">Department / Track</span>
              <input
                type="text"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                className="mt-1.5 w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-base dark:border-slate-700 dark:bg-slate-800"
              />
            </label>

            {user?.role === 'student' && (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <label className="block">
                  <span className="text-sm font-semibold">Education Stage</span>
                  <select
                    value={educationStage || '12th'}
                    onChange={(e) => setEducationStage(e.target.value as '10th' | '12th')}
                    className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-base dark:border-slate-700 dark:bg-slate-800"
                  >
                    <option value="10th">10th Pass-Out</option>
                    <option value="12th">12th Pass-Out</option>
                    <option value="college">College</option>
                  </select>
                </label>

                <label className="block">
                  <span className="text-sm font-semibold">Stream</span>
                  <select
                    value={stream || 'Science (PCM)'}
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
              </div>
            )}

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <label className="block">
                <span className="text-sm font-semibold">Theme Mode</span>
                <select
                  value={theme}
                  onChange={(e) => setThemeMode(e.target.value as 'light' | 'dark')}
                  className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-base dark:border-slate-700 dark:bg-slate-800"
                >
                  <option value="light">Light Mode</option>
                  <option value="dark">Dark Mode</option>
                </select>
              </label>

              <label className="block">
                <span className="text-sm font-semibold">Language</span>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-base dark:border-slate-700 dark:bg-slate-800"
                >
                  <option value="en">English</option>
                  <option value="hi">Hindi (हिन्दी)</option>
                  <option value="mr">Marathi (मराठी)</option>
                </select>
              </label>
            </div>

            <label className="flex items-center justify-between rounded-xl border border-slate-200 p-4 dark:border-slate-700">
              <div>
                <p className="text-base font-semibold">Smart Alerts &amp; Notifications</p>
                <p className="text-sm text-slate-500">
                  Attendance alerts, exam deadlines, and new AI career updates
                </p>
              </div>
              <input
                type="checkbox"
                checked={notificationsEnabled}
                onChange={(e) => setNotificationsEnabled(e.target.checked)}
                className="h-5 w-5 accent-[#7B2D8E]"
              />
            </label>

            {saved && (
              <p className="rounded-xl bg-emerald-50 px-4 py-2.5 text-sm font-semibold text-emerald-700">
                {saved}
              </p>
            )}

            <button
              type="submit"
              disabled={saving}
              className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[#FF7A45] to-[#FF5163] py-3.5 text-base font-bold text-white shadow-sm hover:brightness-105 disabled:opacity-60"
            >
              <Save className="h-5 w-5" aria-hidden="true" />
              <span>{saving ? 'Saving...' : 'Save Settings'}</span>
            </button>
          </form>
        </Card>
      </div>
    </AppShell>
  )
}
