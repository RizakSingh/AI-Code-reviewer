import { useQuery } from "@tanstack/react-query"
import { Link, useParams } from "react-router-dom"
import { api } from "../api/client"
import type { PullRequest, Severity } from "../api/types"
import { StatusBadge } from "../components/StatusBadge"
import { SeverityBadge } from "../components/SeverityBadge"
import { Spinner } from "../components/Spinner"

const SEVERITY_ORDER: Severity[] = ["critical", "warning", "info"]

export function PullRequestDetailPage() {
  const { prId } = useParams<{ prId: string }>()

  const { data: pr, isLoading, isError } = useQuery({
    queryKey: ["pull-request", prId],
    queryFn: () => api.get<PullRequest>(`/api/reviews/pull-request/${prId}`),
    refetchInterval: (query) =>
      query.state.data?.status === "pending" || query.state.data?.status === "reviewing"
        ? 3000
        : false,
  })

  if (isLoading) {
    return (
      <div className="flex justify-center py-16">
        <Spinner />
      </div>
    )
  }

  if (isError || !pr) {
    return (
      <p className="rounded-lg border border-rose-200 bg-rose-50/70 px-4 py-3 text-sm text-rose-700 backdrop-blur">
        Couldn't load this pull request.
      </p>
    )
  }

  const review = pr.reviews[pr.reviews.length - 1]
  const sortedIssues = review
    ? [...review.issues_found].sort(
        (a, b) => SEVERITY_ORDER.indexOf(a.severity) - SEVERITY_ORDER.indexOf(b.severity),
      )
    : []

  return (
    <div>
      <Link to="/" className="text-sm font-medium text-indigo-600 hover:text-fuchsia-600">
        ← Back to repos
      </Link>

      <div className="mt-2 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">
            #{pr.pr_number} {pr.title}
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Opened by {pr.author} · {new Date(pr.created_at).toLocaleString()}
          </p>
        </div>
        <StatusBadge status={pr.status} />
      </div>

      <div className="mt-6">
        {(pr.status === "pending" || pr.status === "reviewing") && (
          <div className="flex items-center gap-3 rounded-xl border border-amber-200 bg-amber-50/70 px-5 py-4 text-sm text-amber-800 backdrop-blur">
            <Spinner className="h-5 w-5 text-amber-500" />
            {pr.status === "pending"
              ? "Queued for review — this updates automatically."
              : "The AI is reviewing this pull request — this updates automatically."}
          </div>
        )}

        {pr.status === "failed" && (
          <div className="rounded-xl border border-rose-200 bg-rose-50/70 px-5 py-4 text-sm text-rose-700 backdrop-blur">
            This review failed after retrying. Check the worker logs, or push a new commit to
            trigger another review.
          </div>
        )}

        {pr.status === "reviewed" && review && (
          <div className="space-y-6">
            <section className="rounded-xl border border-white/50 bg-white/50 p-5 shadow-sm backdrop-blur-xl">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-indigo-500">
                Summary
              </h2>
              <p className="mt-2 text-slate-800">
                {review.ai_summary || "No summary was returned."}
              </p>
            </section>

            <section className="rounded-xl border border-white/50 bg-white/50 p-5 shadow-sm backdrop-blur-xl">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-fuchsia-500">
                Issues found ({sortedIssues.length})
              </h2>
              {sortedIssues.length === 0 ? (
                <p className="mt-2 text-sm text-slate-500">No issues found. Nice work!</p>
              ) : (
                <ul className="mt-3 space-y-3">
                  {sortedIssues.map((issue, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm">
                      <SeverityBadge severity={issue.severity} />
                      <span className="text-slate-700">
                        {issue.line != null && (
                          <span className="mr-1.5 font-mono text-xs text-slate-400">
                            L{issue.line}
                          </span>
                        )}
                        {issue.message}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <section className="rounded-xl border border-white/50 bg-white/50 p-5 shadow-sm backdrop-blur-xl">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-cyan-500">
                Suggestions
              </h2>
              {review.suggestions.length === 0 ? (
                <p className="mt-2 text-sm text-slate-500">No suggestions.</p>
              ) : (
                <ul className="mt-3 list-disc space-y-1.5 pl-5 text-sm text-slate-700">
                  {review.suggestions.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              )}
            </section>
          </div>
        )}
      </div>
    </div>
  )
}
