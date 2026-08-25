# AI Code Review Assistant

A FastAPI backend that automatically reviews GitHub pull requests using an
LLM — posts inline feedback as a bot comment the moment a PR is opened,
without a human reviewer having to be online.

## 🚀 Live Demo

- **Frontend**: https://ai-code-reviewer-theta-dun.vercel.app
- **Backend API**: https://ai-code-reviewer-565p.onrender.com
- **API Docs (Swagger)**: https://ai-code-reviewer-565p.onrender.com/docs

Deployed on free-tier infrastructure end-to-end (see [Deployment](#deployment) below).

## Features

- **GitHub OAuth** login + **webhook auto-registration** per repo
- **HMAC-SHA256 webhook signature verification** (constant-time comparison —
  rejects forged payloads)
- **Idempotent webhook handling** via GitHub's delivery ID — safe against
  GitHub's automatic retries
- **Async background processing** (Celery + Redis) — webhook responds
  instantly; the actual LLM call happens off the request path, so GitHub's
  10s webhook timeout is never at risk
- **Automatic retry** on task failure (`max_retries=3`) with PR status
  tracking (`pending -> reviewing -> reviewed/failed`)
- **Multi-provider AI abstraction**: reviews run on **Groq** (Llama 3.3 70B)
  by default for free, fast inference, with a config-only switch to
  **Anthropic (Claude)** for production-grade review quality
  (`AI_PROVIDER=groq|anthropic`)
- **Structured AI output**: summary + categorized issues + suggestions,
  posted back to GitHub as a formatted comment
- **PostgreSQL + SQLAlchemy** relational schema (users -> repos -> pull
  requests -> reviews), connection pooling with `pool_pre_ping`
- **Alembic migrations**
- **Paginated PR/review history API**
- **Dockerized**: single-container deploy (API + Celery worker share one
  process via `start.sh`) for free-tier hosting, or separate API/worker
  containers via `docker-compose` for local development
- **Tests**: pytest suite for webhook signature verification, AI response
  parsing, and session token issuance/validation (14 tests, no external
  services required)
- **Session auth**: GitHub OAuth token is exchanged server-side for a
  short-lived JWT, handed to the frontend once via the callback redirect and
  sent back as a `Bearer` token thereafter - `/api/reviews/*` endpoints
  require it and are scoped to the caller's own repos

## Tech Stack

| Layer | Tech |
|---|---|
| API | FastAPI, Uvicorn |
| Database | PostgreSQL, SQLAlchemy, Alembic |
| Background jobs | Celery, Redis |
| Auth | GitHub OAuth |
| AI | Groq (Llama 3.3 70B) / Anthropic (Claude) — switchable |
| GitHub integration | PyGithub |
| Frontend | React + Vite + TypeScript |
| Containerization | Docker |

## Deployment

Deployed entirely on free tiers, with zero monthly cost:

| Component | Where | Notes |
|---|---|---|
| Frontend | **Vercel** | Static SPA build, auto-deploys on push, `vercel.json` rewrite rule for client-side routing |
| Backend API + Celery Worker | **Render** (Web Service, Docker) | Both processes run in a **single free container** — `start.sh` launches the Celery worker in the background and Uvicorn in the foreground, since Render's free tier only offers one free web service instance (Background Workers are paid) |
| PostgreSQL | **Render Postgres** (free tier) | Migrations run automatically on every deploy via `alembic upgrade head` in `start.sh` |
| Redis | **Render Key Value** (free tier) | Used as both the Celery broker and result backend |
| Keep-alive | **UptimeRobot** | Pings `/health` every 5 minutes so the free Render instance never hits its 15-minute inactivity sleep — avoids cold starts |

### Single-container API + worker trick

Render's free tier doesn't include Background Worker services, so both
processes run in the same container:

```bash
#!/bin/sh
# start.sh
echo "Running database migrations..."
alembic upgrade head

echo "Starting celery worker..."
celery -A app.celery_app.celery_app worker --loglevel=info &

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
```

For local development or a paid production setup, `docker-compose.yml` /
`Dockerfile.worker` still define a proper separate API+worker split.

## Quick Start (Docker — recommended for local dev)

```bash
cp .env.example .env    # fill in GitHub OAuth app + Groq/Anthropic key
docker compose up --build
```

- API: http://localhost:8000
- Interactive docs (Swagger): http://localhost:8000/docs

## Manual Setup

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env   # requires local Postgres + Redis running

# run migrations
venv/bin/alembic revision --autogenerate -m "init"
venv/bin/alembic upgrade head

# run API
venv/bin/uvicorn app.main:app --reload

# run worker (separate terminal)
venv/bin/celery -A app.celery_app.celery_app worker --loglevel=info
```

## Running Tests
```bash
venv/bin/python -m pytest tests/ -v
```

## AI Provider Configuration

Set in `.env`:
AI_PROVIDER=groq # or "anthropic"
GROQ_API_KEY=your_key # free tier at console.groq.com
ANTHROPIC_API_KEY=your_key # only needed if AI_PROVIDER=anthropic


## Setting Up a GitHub OAuth App + Webhook

1. GitHub → Settings → Developer settings → OAuth Apps → New OAuth App
2. **Homepage URL**: your frontend URL (e.g. the Vercel deployment)
3. **Authorization callback URL**: `<your-backend-url>/api/auth/github/callback`
4. Copy Client ID/Secret into `.env` / your host's environment variables
5. A user logs in by hitting `/api/auth/github/login`, authorizing on GitHub,
   and following the redirect back to `/api/auth/github/callback`. The
   callback upserts the user, mints a short-lived session JWT, and redirects
   the browser to `CLIENT_URL/?token=<jwt>` - the raw GitHub token never
   reaches the browser. The frontend reads that query param once, stores the
   JWT itself (e.g. `localStorage`), and sends it as `Authorization: Bearer
   <jwt>` on every subsequent request (a query-param handoff instead of an
   httpOnly cookie, since the frontend may be hosted on a different
   origin/scheme than this API - cross-site cookies need `SameSite=None` +
   `Secure`, which requires an HTTPS backend). From there:
   - `GET /api/auth/me` - who's logged in
   - `POST /api/reviews/repo` with JSON body `{"repo_name": "..."}` -
     registers a repo owned by the logged-in user (bearer token required)
   - `GET /api/reviews/repos` - lists the logged-in user's registered repos
6. Point a webhook at `POST /api/webhooks/github` for the `pull_request`
   event, using `GITHUB_WEBHOOK_SECRET` as the shared secret
   (`github_service.register_webhook` can do this programmatically too)

## Alternative: Deploying to AWS (production-scale path)

1. Push `api` and `worker` images to **ECR**
2. Run both as separate **ECS Fargate** services (they scale independently —
   more worker tasks under review load, without touching the API tier)
3. **RDS PostgreSQL** instead of Render Postgres
4. **ElastiCache (Redis)** as the Celery broker/result backend
5. **ALB** in front of the API service for TLS termination + horizontal scaling
6. Store secrets (GitHub secret, AI provider key) in **AWS Secrets Manager**,
   injected as task environment variables

## Why this design (for interviews)

- **Webhook decoupling via Celery**: the single most important design
  decision here. Webhooks must respond within ~10 seconds or GitHub marks
  them failed and retries — an LLM call can easily take longer, so the
  webhook only validates + enqueues, and a separate worker does the slow work.
- **Idempotency via delivery ID**: GitHub retries webhooks it doesn't get a
  fast 2xx for. Without a dedup check, a slow-but-successful first response
  would cause duplicate reviews on retry.
- **Signature verification with `hmac.compare_digest`**: a naive `==`
  string comparison leaks timing information that can be exploited to
  forge a valid signature byte-by-byte; constant-time comparison closes that.
- **Retry + status tracking**: transient failures (rate limits, network
  blips) auto-retry up to 3 times; the PR's `status` field gives visibility
  into what's actually happening instead of silent failures.
- **Multi-provider AI abstraction**: swapping Groq for Anthropic (or any
  other provider) is a one-line env var change, not a code change — keeps
  the system usable on a free tier while staying production-upgradeable.
- **Single-container deploy trade-off**: running API + worker in one
  process is a deliberate free-tier constraint, not the default architecture
  — documented here so it reads as an informed choice rather than an
  oversight; `docker-compose.yml` shows the properly separated version.