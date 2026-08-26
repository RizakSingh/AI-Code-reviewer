import { Link, Outlet } from "react-router-dom"
import { useAuth } from "../auth/AuthContext"
import { Aurora } from "./Aurora"

export function Layout() {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen">
      <Aurora />
      <header className="sticky top-0 z-10 border-b border-white/40 bg-white/50 shadow-sm backdrop-blur-xl">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <Link to="/" className="flex items-center gap-2 font-semibold text-slate-900">
            <span className="text-xl">🤖</span>
            <span className="bg-linear-to-r from-indigo-600 via-fuchsia-600 to-cyan-600 bg-clip-text text-transparent">
              AI Code Reviewer
            </span>
          </Link>
          {user && (
            <div className="flex items-center gap-4 text-sm">
              <span className="text-slate-500">
                Signed in as <span className="font-medium text-slate-800">{user.username}</span>
              </span>
              <button
                onClick={logout}
                className="rounded-md border border-white/60 bg-white/40 px-3 py-1.5 font-medium text-slate-600 backdrop-blur transition hover:border-slate-300 hover:bg-white/70 hover:text-slate-900"
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
