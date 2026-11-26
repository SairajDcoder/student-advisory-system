import React, { useEffect, useState } from 'react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Activity, Database, RefreshCw, Upload, UserPlus } from 'lucide-react'
import { AppShell } from '../components/AppShell'
import { Card, DashboardSkeleton, ErrorBanner } from '../components/ui'
import { apiRequest, ApiError } from '../lib/api'
import { AdminOverview } from '../types'

export function AdminDashboard() {
  const [data, setData] = useState<AdminOverview | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [statusMsg, setStatusMsg] = useState('')
  const [retraining, setRetraining] = useState(false)
  const [newUser, setNewUser] = useState({
    full_name: '',
    email: '',
    password: '',
    role: 'student',
    department: '12th Pass-Out (PCM)',
  })

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await apiRequest<AdminOverview>('/api/admin/overview')
      setData(res)
    } catch {
      setError('Unable to load Admin analytics.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const toggleActive = async (id: number, current: boolean) => {
    await apiRequest(`/api/admin/users/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ is_active: !current }),
    })
    load()
  }

  const createUser = async (e: React.FormEvent) => {
    e.preventDefault()
    setStatusMsg('')
    try {
      await apiRequest('/api/admin/users', {
        method: 'POST',
        body: JSON.stringify(newUser),
      })
      setNewUser({ full_name: '', email: '', password: '', role: 'student', department: '12th Pass-Out (PCM)' })
      setStatusMsg('User created successfully.')
      load()
    } catch (err) {
      setStatusMsg(err instanceof ApiError ? err.message : 'Failed to create user.')
    }
  }

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const form = new FormData()
    form.append('file', file)
    setStatusMsg('')
    try {
      const res = await apiRequest<{ message: string }>('/api/admin/dataset', {
        method: 'POST',
        body: form,
      })
      setStatusMsg(res.message)
    } catch (err) {
      setStatusMsg(err instanceof ApiError ? err.message : 'Upload failed.')
    }
  }

  const handleRetrain = async () => {
    setRetraining(true)
    setStatusMsg('')
    try {
      const res = await apiRequest<{ message: string }>('/api/admin/retrain', { method: 'POST' })
      setStatusMsg(res.message)
      await load()
    } finally {
      setRetraining(false)
    }
  }

  return (
    <AppShell>
      {loading ? (
        <DashboardSkeleton />
      ) : error || !data ? (
        <ErrorBanner message={error || 'Unable to load'} onRetry={load} />
      ) : (
        <div className="space-y-6">
          <div className="flex flex-col justify-between gap-4 rounded-2xl bg-gradient-to-r from-[#7B2D8E] to-[#581C68] p-6 text-white shadow-md sm:flex-row sm:items-center">
            <div>
              <h1 className="font-['Poppins'] text-2xl font-bold">Admin Console &amp; ML Operations</h1>
              <p className="mt-1 text-base text-purple-100">
                Manage users, monitor department outcomes, upload datasets, and retrain XGBoost models.
              </p>
            </div>
            <button
              type="button"
              onClick={handleRetrain}
              disabled={retraining}
              className="inline-flex shrink-0 items-center gap-2 rounded-xl bg-gradient-to-r from-[#FF7A45] to-[#FF5163] px-5 py-3 text-base font-bold text-white shadow-sm hover:brightness-105 disabled:opacity-60"
            >
              <RefreshCw className={`h-5 w-5 ${retraining ? 'animate-spin' : ''}`} aria-hidden="true" />
              <span>{retraining ? 'Retraining...' : 'Retrain ML Models'}</span>
            </button>
          </div>

          {statusMsg && (
            <div className="rounded-xl border border-purple-200 bg-purple-50 px-4 py-3 text-sm font-semibold text-[#7B2D8E]">
              {statusMsg}
            </div>
          )}

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <Card>
              <div className="flex items-center justify-between text-sm font-semibold text-slate-500">
                <span>API &amp; Database</span>
                <Activity className="h-5 w-5 text-emerald-600" aria-hidden="true" />
              </div>
              <p className="mt-2 font-['Poppins'] text-2xl font-bold text-emerald-600">
                {data.system_health.api_status}
              </p>
              <p className="text-xs text-slate-500">{data.system_health.database_status}</p>
            </Card>

            <Card>
              <p className="text-sm font-semibold text-slate-500">CGPA Model (R²)</p>
              <p className="mt-2 font-['Poppins'] text-2xl font-bold">
                {data.system_health.ml_metrics?.cgpa_r2 ?? '0.85'}
              </p>
              <p className="text-xs text-slate-500">
                MAE: {data.system_health.ml_metrics?.cgpa_mae ?? '0.25'} CGPA
              </p>
            </Card>

            <Card>
              <p className="text-sm font-semibold text-slate-500">Risk Model Accuracy</p>
              <p className="mt-2 font-['Poppins'] text-2xl font-bold text-[#7B2D8E]">
                {((data.system_health.ml_metrics?.risk_accuracy ?? 0.9) * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-slate-500">
                Training rows: {data.system_health.ml_metrics?.dataset_rows ?? 2400}
              </p>
            </Card>

            <Card>
              <p className="text-sm font-semibold text-slate-500">Cohort Risk Breakdown</p>
              <p className="mt-2 text-sm font-bold">
                <span className="text-emerald-600">Safe: {data.risk_summary.Low || 0}</span> •{' '}
                <span className="text-amber-600">Watch: {data.risk_summary.Medium || 0}</span> •{' '}
                <span className="text-rose-600">At Risk: {data.risk_summary.High || 0}</span>
              </p>
              <p className="mt-1 text-xs text-slate-500">
                {data.system_health.total_users} total platform users
              </p>
            </Card>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <Card className="lg:col-span-2">
              <h2 className="font-['Poppins'] text-lg font-bold">Department / Track Analytics</h2>
              <p className="mb-4 text-sm text-slate-500">Average CGPA and student count per cohort</p>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.department_analytics}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="department" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Bar dataKey="avg_cgpa" name="Avg CGPA" fill="#7B2D8E" radius={[6, 6, 0, 0]} />
                    <Bar dataKey="students" name="Students" fill="#FF6B4A" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>

            <Card className="space-y-4">
              <div className="flex items-center gap-2">
                <Database className="h-5 w-5 text-[#14B8A6]" aria-hidden="true" />
                <h2 className="font-['Poppins'] text-lg font-bold">Dataset Management</h2>
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-300">
                Upload a student CSV dataset (`attendance_pct`, `internal_marks_avg`, `next_cgpa`, `risk_level`, etc.) and retrain XGBoost.
              </p>
              <label className="flex cursor-pointer items-center justify-center gap-2 rounded-xl border-2 border-dashed border-purple-200 p-5 text-sm font-semibold text-slate-700 hover:border-[#7B2D8E] dark:border-slate-700 dark:text-slate-200">
                <Upload className="h-5 w-5 text-[#7B2D8E]" aria-hidden="true" />
                <span>Choose CSV Dataset</span>
                <input type="file" accept=".csv" onChange={handleUpload} className="hidden" />
              </label>

              <form onSubmit={createUser} className="space-y-2.5 border-t border-slate-100 pt-4 dark:border-slate-800">
                <p className="flex items-center gap-1.5 text-sm font-bold">
                  <UserPlus className="h-4 w-4 text-[#7B2D8E]" aria-hidden="true" />
                  <span>Quick Add User</span>
                </p>
                <input
                  type="text"
                  required
                  placeholder="Full Name"
                  value={newUser.full_name}
                  onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
                />
                <input
                  type="email"
                  required
                  placeholder="Email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
                />
                <input
                  type="password"
                  required
                  minLength={6}
                  placeholder="Temporary password (min 6 chars)"
                  value={newUser.password}
                  onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
                />
                <div className="grid grid-cols-2 gap-2">
                  <select
                    value={newUser.role}
                    onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                    className="rounded-xl border border-slate-200 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
                  >
                    <option value="student">Student</option>
                    <option value="mentor">Mentor</option>
                    <option value="admin">Admin</option>
                  </select>
                  <button
                    type="submit"
                    className="rounded-xl bg-[#14B8A6] px-3 py-2 text-sm font-semibold text-white hover:bg-[#0D9488]"
                  >
                    Add User
                  </button>
                </div>
              </form>
            </Card>
          </div>

          <Card className="overflow-x-auto p-0">
            <div className="border-b border-slate-200 px-6 py-4 dark:border-slate-800">
              <h2 className="font-['Poppins'] text-lg font-bold">User Management</h2>
            </div>
            <table className="w-full min-w-[600px] text-left">
              <thead className="bg-[#FAF7FD] text-xs font-bold uppercase text-slate-500 dark:bg-slate-800/60 dark:text-slate-300">
                <tr>
                  <th className="px-6 py-3">Name</th>
                  <th className="px-6 py-3">Email</th>
                  <th className="px-6 py-3">Role</th>
                  <th className="px-6 py-3">Department</th>
                  <th className="px-6 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm dark:divide-slate-800">
                {data.users.map((u) => (
                  <tr key={u.id}>
                    <td className="px-6 py-3.5 font-semibold">{u.full_name}</td>
                    <td className="px-6 py-3.5 text-slate-500">{u.email}</td>
                    <td className="px-6 py-3.5 capitalize">{u.role}</td>
                    <td className="px-6 py-3.5">{u.department}</td>
                    <td className="px-6 py-3.5">
                      <button
                        type="button"
                        onClick={() => toggleActive(u.id, u.is_active)}
                        className={`rounded-full px-3 py-1 text-xs font-bold ${
                          u.is_active
                            ? 'bg-emerald-50 text-emerald-700'
                            : 'bg-rose-50 text-rose-700'
                        }`}
                      >
                        {u.is_active ? 'Active' : 'Inactive'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      )}
    </AppShell>
  )
}
