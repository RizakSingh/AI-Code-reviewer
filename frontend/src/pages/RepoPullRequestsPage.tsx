import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Link, useParams } from "react-router-dom"
import { api } from "../api/client"
import type { PullRequest, Repo } from "../api/types"
import { StatusBadge } from "../components/StatusBadge"
import { Spinner } from "../components/Spinner"

const PAGE_SIZE = 20

export function RepoPullRequestsPage() {
  const { repoId } = useParams<{ repoId: string }>()
  const [page, setPage] = useState(1)

  const { data: repos } = useQuery({
    queryKey: ["repos"],
    queryFn: () => api.get<Repo[]>("/api/reviews/repos"),
  })
  const repo = repos?.find((r) => r.id === Number(repoId))

  const { data: pullRequests, isLoading, isError } = useQuery({
    queryKey: ["pull-requests", repoId, page],
    queryFn: () =>
      api.get<PullRequest[]>(
        `/api/reviews/repo/${repoId}/pull-requests?page=${page}&limit=${PAGE_SIZE}`,
      ),
    refetchInterval: (query) =>
      query.state.data?.some((pr) => pr.status === "pending" || pr.status === "reviewing")
        ? 4000
        : false,
  })

  return (
    <div>
      <Link to="/" className="text-sm font-medium text-indigo-600 hover:text-fuchsia-600">
        ← All repos
      </Link>
      <h1 className="mt-2 text-2xl font-semibold text-slate-900">
        {repo?.repo_name ?? "Pull requests"}
      </h1>

      <div className="mt-6">
        {isLoading && (
          <div className="flex justify-center py-16">
            <Spinner />
          </div>
        )}

        {isError && (
          <p className="rounded-lg border border-rose-200 bg-rose-50/70 px-4 py-3 text-sm text-rose-700 backdrop-blur">
            Couldn't load pull requests for this repo.
          </p>
        )}

        {pullRequests && pullRequests.length === 0 && page === 1 && (
          <div className="rounded-xl border border-dashed border-slate-300 bg-white/50 px-6 py-16 text-center text-slate-500 backdrop-blur-xl">
            No pull requests reviewed yet. Open a PR on this repo to see it show up here.
          </div>
        )}

        {pullRequests && pullRequests.length > 0 && (
          <ul className="divide-y divide-white/50 overflow-hidden rounded-xl border border-white/50 bg-white/50 shadow-sm backdrop-blur-xl">
            {pullRequests.map((pr) => (
              <li key={pr.id}>
                <Link
                  to={`/pull-requests/${pr.id}`}
                  className="flex items-center justify-between gap-4 px-4 py-3.5 transition hover:bg-white/70"
                >
                  <div className="min-w-0">
                    <p className="truncate font-medium text-slate-900">
                      #{pr.pr_number} {pr.title}
                    </p>
                    <p className="mt-0.5 text-xs text-slate-500">
                      by {pr.author} · {new Date(pr.created_at).toLocaleString()}
                    </p>
                  </div>
                  <StatusBadge status={pr.status} />
                </Link>
              </li>
            ))}
          </ul>
        )}

        {pullRequests && (pullRequests.length === PAGE_SIZE || page > 1) && (
          <div className="mt-4 flex items-center justify-between text-sm">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="rounded-md border border-white/60 bg-white/50 px-3 py-1.5 font-medium text-slate-600 backdrop-blur transition hover:bg-white/70 disabled:cursor-not-allowed disabled:opacity-40"
            >
              ← Previous
            </button>
            <span className="text-slate-500">Page {page}</span>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={pullRequests.length < PAGE_SIZE}
              className="rounded-md border border-white/60 bg-white/50 px-3 py-1.5 font-medium text-slate-600 backdrop-blur transition hover:bg-white/70 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Next →
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
