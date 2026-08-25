import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import { api, ApiError } from "../api/client"
import type { User } from "../api/types"
import { clearToken, setToken } from "./token"

interface AuthState {
  user: User | null
  loading: boolean
  login: () => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // The OAuth callback redirects here with ?token=... instead of a cookie -
    // cross-site cookies can't be relied on when the frontend and backend
    // are hosted on different origins/schemes (e.g. a deployed frontend
    // talking to a local backend).
    const params = new URLSearchParams(window.location.search)
    const token = params.get("token")
    if (token) {
      setToken(token)
      params.delete("token")
      const rest = params.toString()
      window.history.replaceState({}, "", window.location.pathname + (rest ? `?${rest}` : ""))
    }

    api
      .get<User>("/api/auth/me")
      .then(setUser)
      .catch((err) => {
        if (!(err instanceof ApiError && err.status === 401)) {
          console.error("Failed to load session", err)
        }
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [])

  async function login() {
    const { authorize_url } = await api.get<{ authorize_url: string }>("/api/auth/github/login")
    window.location.href = authorize_url
  }

  function logout() {
    clearToken()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}
