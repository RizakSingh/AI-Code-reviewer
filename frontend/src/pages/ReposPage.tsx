import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Link } from "react-router-dom"
import { api } from "../api/client"
import type { Repo } from "../api/types"
import { AddRepoModal } from "../components/AddRepoModal"
import { Spinner } from "../components/Spinner"

export function ReposPage() {
  const [showAddModal, setShowAddModal] = useState(false)

  const { data: repos, isLoading, isError } = useQuery({
    queryKey: ["repos"],
    queryFn: () => api.get<Repo[]>("/api/reviews/repos"),
  })

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Your repos</h1>
          <p className="mt-1 text-sm text-slate-500">
            Pull requests opened on these repos get reviewed automatically.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-1.5 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800"
        >
          <span className="text-base leading-none">+</span> Add repo
        </button>
      </div>

      <div className="mt-6">
        {isLoading && (
          <div className="flex justify-center py-16">
            <Spinner />
          </div>
        )}

        {isError && (
          <p className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            Couldn't load your repos. Try refreshing the page.
          </p>
        )}

        {repos && repos.length === 0 && (
          <div className="rounded-xl border border-dashed border-slate-300 bg-white px-6 py-16 text-center">
            <p className="text-slate-500">No repos connected yet.</p>
            <button
              onClick={() => setShowAddModal(true)}
              className="mt-3 font-medium text-slate-900 underline underline-offset-4 hover:text-slate-700"
            >
              Connect your first repo
            </button>
          </div>
        )}

        {repos && repos.length > 0 && (
          <ul className="grid gap-3 sm:grid-cols-2">
            {repos.map((repo) => (
              <li key={repo.id}>
                <Link
                  to={`/repos/${repo.id}`}
                  className="block rounded-xl border border-slate-200 bg-white p-4 transition hover:border-slate-300 hover:shadow-sm"
                >
                  <p className="font-medium text-slate-900">{repo.repo_name}</p>
                  <p className="mt-1 text-xs text-slate-400">
                    Connected {new Date(repo.created_at).toLocaleDateString()}
                  </p>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>

      {showAddModal && <AddRepoModal onClose={() => setShowAddModal(false)} />}
    </div>
  )
}
