# llm-lens — Agent Guidance

Dashboard for monitoring LLM API calls: FastAPI backend + PostgreSQL/TimescaleDB + Next.js 14 dashboard, with a Python SDK for tracking calls.

## Stack

| Layer | Tech | Where |
|---|---|---|
| Backend API | FastAPI (Python 3.11), SQLAlchemy 2 async, asyncpg, Uvicorn | `backend/` |
| Database | PostgreSQL 15 (TimescaleDB image in compose; vanilla PG works — see notes) | `docker-compose.yml` |
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind, Recharts | `frontend/` |
| SDK/demo | Decorator-based `LLMMonitor` Python SDK + seed demo | `backend/app/monitor/sdk.py`, `examples/` |

## Commands

Package managers: pip (backend venv), npm (frontend). Docker Compose is the documented path; see "Local dev without Docker" for the sandbox-proven path.

```bash
# Full stack (needs Docker)
docker-compose up
# → frontend http://localhost:3000, backend http://localhost:8000, db :5432

# Local dev without Docker (proven in sandbox)
# 1. Postgres: any instance; create db `llm_monitor`, user postgres/postgres
sudo service postgresql start
sudo -u postgres psql -c "CREATE DATABASE llm_monitor;"

# 2. Backend (venv created with `uv venv --python 3.11 backend/venv`)
cd backend
DATABASE_URL='postgresql+asyncpg://postgres:postgres@localhost:5432/llm_monitor' \
  ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. Frontend
cd frontend && npm install && NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev  # port 3000

# Seed demo data through the SDK (backend must be running)
PYTHONPATH=$(pwd)/backend ./backend/venv/bin/python examples/demo.py
```

Ports (parse from startup output, don't assume): backend 8000, frontend 3000, postgres 5432.

## Environment variables

| Var | Used by | Example |
|---|---|---|
| `DATABASE_URL` | backend | `postgresql+asyncpg://postgres:postgres@localhost:5432/llm_monitor` |
| `NEXT_PUBLIC_API_URL` | frontend | `http://localhost:8000` |

No `.env.example` in repo; values above from README + docker-compose.yml. No required API keys.

## Known quirks (do not "fix" blindly)

- **Schema creation rolls back on vanilla Postgres.** `init_db()` (`backend/app/database.py`) runs `CREATE EXTENSION timescaledb` in the same transaction as `create_all`; the failed statement poisons the transaction and silently rolls back table creation on non-TimescaleDB Postgres. Workaround used in sandbox: pre-create the schema (`run_sync(Base.metadata.create_all)` alone, or run once against TimescaleDB). Then app startup is fine.
- **`frontend/lib` was gitignored** by the Python `lib/` rule — that's why `@/lib/api` was missing from the repo. Fixed on the onboarding branch with `!frontend/lib/` negations.
- Lint: `npm run lint` (next lint) has no ESLint config in-repo and prompts interactively. No backend lint/test config.

## Codebase map

See [codebase-map.md](codebase-map.md).

## Local verification

1. `curl localhost:8000/health` → `{"status":"healthy"}`
2. `curl -X POST localhost:8000/api/events -H 'Content-Type: application/json' -d '{"timestamp":"<now ISO>","model":"gpt-4","prompt_tokens":10,"completion_tokens":5,"total_tokens":15,"latency_ms":100,"status":"success"}'` → returns event JSON
3. `curl 'localhost:8000/api/metrics/overview?hours=24'` → totals JSON
4. Dashboard `http://localhost:3000` renders "LLM Monitor Dashboard" with stats cards; headless Playwright check:
   `backend/venv/bin/python` + `playwright` (`chromium.launch()` → `goto localhost:3000`) — title `LLM Monitor Dashboard`.
5. Typecheck: `cd frontend && npx tsc --noEmit` (exit 0 expected). Backend has no typecheck/lint/test suite.

## Sandbox snapshot

- Snapshot ID: `ksfle1i0fwtb5p1kntry:default`
- Captured: 2026-09-24T19:14:26.075Z
- State: Postgres 17 running (service), backend on :8000 and frontend on :3000 in tmux sessions `llmlens` / `llmfront`, Python 3.11 venv at `backend/venv` (via uv), node_modules installed.
