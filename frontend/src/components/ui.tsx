import React from 'react'
import { AlertCircle, CheckCircle2, ShieldAlert } from 'lucide-react'

export function Card({
  children,
  className = '',
}: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <div
      className={`rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm transition-shadow hover:shadow-md dark:border-slate-800 dark:bg-slate-900 ${className}`}
    >
      {children}
    </div>
  )
}

export function RiskBadge({ risk }: { risk: 'Low' | 'Medium' | 'High' | string }) {
  if (risk === 'Low') {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1 text-sm font-semibold text-emerald-700 ring-1 ring-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:ring-emerald-800">
        <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
        Safe (Low Risk)
      </span>
    )
  }
  if (risk === 'Medium') {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-3 py-1 text-sm font-semibold text-amber-800 ring-1 ring-amber-200 dark:bg-amber-950/60 dark:text-amber-300 dark:ring-amber-800">
        <AlertCircle className="h-4 w-4" aria-hidden="true" />
        Watch (Medium)
      </span>
    )
  }
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-50 px-3 py-1 text-sm font-semibold text-rose-700 ring-1 ring-rose-200 dark:bg-rose-950/60 dark:text-rose-300 dark:ring-rose-800">
      <ShieldAlert className="h-4 w-4" aria-hidden="true" />
      At Risk (High)
    </span>
  )
}

export function SkeletonCard() {
  return (
    <div className="animate-pulse rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
      <div className="h-4 w-28 rounded bg-slate-200 dark:bg-slate-800" />
      <div className="mt-4 h-8 w-24 rounded bg-slate-200 dark:bg-slate-800" />
      <div className="mt-3 h-3 w-40 rounded bg-slate-100 dark:bg-slate-800/70" />
    </div>
  )
}

export function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="h-10 w-64 animate-pulse rounded-xl bg-slate-200 dark:bg-slate-800" />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="h-72 animate-pulse rounded-2xl bg-slate-200 lg:col-span-2 dark:bg-slate-800" />
        <div className="h-72 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-800" />
      </div>
    </div>
  )
}

export function ErrorBanner({
  message,
  onRetry,
}: {
  message: string
  onRetry?: () => void
}) {
  return (
    <div
      role="alert"
      className="flex flex-col items-start justify-between gap-4 rounded-2xl border border-rose-200 bg-rose-50 p-5 text-rose-900 sm:flex-row sm:items-center dark:border-rose-900 dark:bg-rose-950/40 dark:text-rose-200"
    >
      <div className="flex items-center gap-3">
        <AlertCircle className="h-6 w-6 shrink-0 text-rose-600 dark:text-rose-400" aria-hidden="true" />
        <p className="text-base font-medium">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="rounded-xl bg-rose-600 px-4 py-2 text-sm font-semibold text-white hover:bg-rose-700"
        >
          Try again
        </button>
      )}
    </div>
  )
}
