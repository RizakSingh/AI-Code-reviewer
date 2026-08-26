import { useState, type FormEvent } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { api, ApiError } from "../api/client"
import type { Repo } from "../api/types"

export function AddRepoModal({ onClose }: { onClose: () => void }) {
  const [repoName, setRepoName] = useState("")
  const [error, setError] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: (repo_name: string) => api.post<Repo>("/api/reviews/repo", { repo_name }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["repos"] })
      onClose()
    },
    onError: (err) => {
      setError(err instanceof ApiError ? err.message : "Something went wrong")
    },
  })

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    const trimmed = repoName.trim()
    if (!/^[^/\s]+\/[^/\s]+$/.test(trimmed)) {
      setError('Use the format "owner/repo", e.g. octocat/hello-world')
      return
    }
    mutation.mutate(trimmed)
  }

  return (
    <div
      className="fixed inset-0 z-10 flex items-center justify-center bg-slate-900/30 px-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-xl border border-white/60 bg-white/70 p-6 shadow-xl shadow-indigo-200/40 backdrop-blur-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-lg font-semibold text-slate-900">Connect a repo</h2>
        <p className="mt-1 text-sm text-slate-500">
          Register a GitHub repo so its pull requests get reviewed automatically.
        </p>
        <form onSubmit={handleSubmit} className="mt-4">
          <label className="block text-sm font-medium text-slate-700" htmlFor="repo_name">
            Repository
          </label>
          <input
            id="repo_name"
            autoFocus
            value={repoName}
            onChange={(e) => setRepoName(e.target.value)}
            placeholder="octocat/hello-world"
            className="mt-1 w-full rounded-md border border-white/70 bg-white/60 px-3 py-2 text-sm backdrop-blur focus:border-fuchsia-400 focus:outline-none focus:ring-1 focus:ring-fuchsia-400"
          />
          {error && <p className="mt-2 text-sm text-rose-600">{error}</p>}
          <div className="mt-5 flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-md px-3 py-2 text-sm font-medium text-slate-600 hover:bg-white/60"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={mutation.isPending || !repoName.trim()}
              className="rounded-md bg-linear-to-r from-indigo-600 via-fuchsia-600 to-cyan-600 px-4 py-2 text-sm font-medium text-white shadow-md shadow-fuchsia-300/40 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {mutation.isPending ? "Connecting…" : "Connect"}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
