export interface User {
  id: number
  username: string
  created_at: string
}

export interface Repo {
  id: number
  repo_name: string
  created_at: string
}

export type Severity = "info" | "warning" | "critical"

export interface Issue {
  line: number | null
  severity: Severity
  message: string
}

export interface Review {
  id: number
  ai_summary: string | null
  issues_found: Issue[]
  suggestions: string[]
  created_at: string
}

export type PullRequestStatus = "pending" | "reviewing" | "reviewed" | "failed"

export interface PullRequest {
  id: number
  pr_number: number
  title: string
  author: string
  status: PullRequestStatus
  created_at: string
  reviews: Review[]
}
