import { useState } from "react"
import { Navigate } from "react-router-dom"
import { useAuth } from "../auth/AuthContext"
import { Aurora } from "../components/Aurora"

export function LoginPage() {
  const { user, loading, login } = useAuth()
  const [redirecting, setRedirecting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!loading && user) return <Navigate to="/" replace />

  async function handleLogin() {
    setRedirecting(true)
    setError(null)
    try {
      await login()
    } catch (err) {
      console.error("Login failed", err)
      setError(
        "Couldn't reach the server. Make sure the backend is running at " +
          (import.meta.env.VITE_API_URL ?? "http://localhost:8000") +
          ".",
      )
      setRedirecting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <Aurora />
      <div className="w-full max-w-sm rounded-2xl border border-white/50 bg-white/50 p-8 text-center shadow-xl shadow-indigo-200/40 backdrop-blur-xl">
        <div className="mb-4 text-4xl">🤖</div>
        <h1 className="bg-linear-to-r from-indigo-600 via-fuchsia-600 to-cyan-600 bg-clip-text text-xl font-semibold text-transparent">
          AI Code Reviewer
        </h1>
        <p className="mt-2 text-sm text-slate-600">
          Automatic, AI-powered feedback on your pull requests the moment they're opened.
        </p>
        <button
          onClick={handleLogin}
          disabled={redirecting || loading}
          className="mt-6 flex w-full items-center justify-center gap-2 rounded-lg bg-linear-to-r from-indigo-600 via-fuchsia-600 to-cyan-600 px-4 py-2.5 font-medium text-white shadow-lg shadow-fuchsia-300/40 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current" aria-hidden="true">
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0016 8c0-4.42-3.58-8-8-8z" />
          </svg>
          {redirecting ? "Redirecting to GitHub…" : "Continue with GitHub"}
        </button>
        {error && <p className="mt-4 text-sm text-rose-600">{error}</p>}
      </div>
    </div>
  )
}
