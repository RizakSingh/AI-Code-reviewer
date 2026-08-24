import type { PullRequestStatus } from "../api/types"

const STYLES: Record<PullRequestStatus, string> = {
  pending: "bg-slate-100 text-slate-600 ring-slate-200",
  reviewing: "bg-amber-50 text-amber-700 ring-amber-200",
  reviewed: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  failed: "bg-rose-50 text-rose-700 ring-rose-200",
}

const LABELS: Record<PullRequestStatus, string> = {
  pending: "Pending",
  reviewing: "Reviewing…",
  reviewed: "Reviewed",
  failed: "Failed",
}

export function StatusBadge({ status }: { status: PullRequestStatus }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset ${STYLES[status]}`}
    >
      {status === "reviewing" && (
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-amber-500" />
      )}
      {LABELS[status]}
    </span>
  )
}
