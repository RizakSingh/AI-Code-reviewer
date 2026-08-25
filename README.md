# AI Code Review Assistant

A FastAPI backend that automatically reviews GitHub pull requests using an
LLM — posts inline feedback as a bot comment the moment a PR is opened,
without a human reviewer having to be online.

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
- **Structured AI output**: summary + categorized issues + suggestions,
  posted back to GitHub as a formatted comment
- **PostgreSQL + SQLAlchemy** relational schema (users -> repos -> pull
  requests -> reviews), connection pooling with `pool_pre_ping`
- **Alembic migrations**
- **Paginated PR/review history API**
- **Dockerized**: separate API and worker containers + Postgres + Redis via
  `docker-compose`
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
| AI | Claude API (Anthropic) |
| GitHub integration | PyGithub |
| Containerization | Docker, docker-compose |

## Quick Start (Docker — recommended)

```bash
cp .env.example .env    # fill in GitHub OAuth app + Anthropic key
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

## Setting Up a GitHub OAuth App + Webhook

1. GitHub → Settings → Developer settings → OAuth Apps → New OAuth App
2. Set callback URL to `GITHUB_CALLBACK_URL` in your `.env`
3. Copy Client ID/Secret into `.env`
4. A user logs in by hitting `/api/auth/github/login`, authorizing on GitHub,
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
5. Point a webhook at `POST /api/webhooks/github` for the `pull_request`
   event, using `GITHUB_WEBHOOK_SECRET` as the shared secret
   (`github_service.register_webhook` can do this programmatically too)

## Deploying to AWS (suggested path)

1. Push `api` and `worker` images to **ECR**
2. Run both as separate **ECS Fargate** services (they scale independently —
   more worker tasks under review load, without touching the API tier)
3. **RDS PostgreSQL** instead of the compose Postgres container
4. **ElastiCache (Redis)** as the Celery broker/result backend
5. **ALB** in front of the API service for TLS termination + horizontal scaling
6. Store secrets (GitHub secret, Anthropic key) in **AWS Secrets Manager**,
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
- **Separate API/worker containers**: lets you scale review throughput
  (add workers) independently of API request capacity.
