import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import { api, ApiError } from "../api/client"
import type { User } from "../api/types"

interface AuthState {
  user: User | null
  loading: boolean
  login: () => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
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

  async function logout() {
    await api.post("/api/auth/logout")
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
