import { Route, Routes } from "react-router-dom"
import { AuthProvider } from "./auth/AuthContext"
import { Layout } from "./components/Layout"
import { ProtectedRoute } from "./components/ProtectedRoute"
import { LoginPage } from "./pages/LoginPage"
import { PullRequestDetailPage } from "./pages/PullRequestDetailPage"
import { RepoPullRequestsPage } from "./pages/RepoPullRequestsPage"
import { ReposPage } from "./pages/ReposPage"

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route path="/" element={<ReposPage />} />
            <Route path="/repos/:repoId" element={<RepoPullRequestsPage />} />
            <Route path="/pull-requests/:prId" element={<PullRequestDetailPage />} />
          </Route>
        </Route>
      </Routes>
    </AuthProvider>
  )
}

export default App
