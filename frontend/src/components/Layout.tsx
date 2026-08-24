import { Link, Outlet } from "react-router-dom"
import { useAuth } from "../auth/AuthContext"

export function Layout() {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <Link to="/" className="flex items-center gap-2 font-semibold text-slate-900">
            <span className="text-xl">🤖</span>
            AI Code Reviewer
          </Link>
          {user && (
            <div className="flex items-center gap-4 text-sm">
              <span className="text-slate-500">
                Signed in as <span className="font-medium text-slate-800">{user.username}</span>
              </span>
              <button
                onClick={logout}
                className="rounded-md border border-slate-300 px-3 py-1.5 font-medium text-slate-600 transition hover:border-slate-400 hover:text-slate-900"
              >
                Log out
              </button>
            </div>
          )}
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  )
}
