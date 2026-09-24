---
name: local-dev
description: How to bring llm-lens up locally (backend, frontend, Postgres) and verify it — captured during automated onboarding 2026-09-24
---

# Local dev — llm-lens

## Goal

FastAPI backend on :8000, Next.js dashboard on :3000, Postgres on :5432, seeded with demo data, dashboard verified in a headless browser.

## Steps that worked in the sandbox

1. **Postgres** (Docker is NOT available in the sandbox; Debian 13 host):
   ```bash
   sudo apt-get update && sudo apt-get install -y postgresql libpq-dev
   sudo service postgresql start
   sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
   sudo -u postgres psql -c "CREATE DATABASE llm_monitor;"
   ```
   Vanilla PG 17, not TimescaleDB (extension not in Debian repos). App degrades gracefully — TimescaleDB-only bits log warnings and are skipped.
2. **Backend deps** — Python here is 3.13, but pinned deps (asyncpg 0.29, psycopg2-binary 2.9.9, pydantic 2.5) have no 3.13 wheels and fail to build. Install `uv` and create a 3.11 venv (README requires Python 3.11+):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   cd backend && ~/.local/bin/uv venv --python 3.11 venv
   ~/.local/bin/uv pip install -p venv/bin/python -r requirements.txt
   ```
3. **Pre-create the schema** (required — see quirk below):
   ```bash
   cd backend && ./venv/bin/python -c "
   import asyncio
   from app import models
   from app.database import Base, engine
   async def main():
       async with engine.begin() as conn:
           await conn.run_sync(Base.metadata.create_all)
   asyncio.run(main())"
   ```
4. **Start backend** (tmux session `llmlens`):
   ```bash
   DATABASE_URL='postgresql+asyncpg://postgres:postgres@localhost:5432/llm_monitor' \
     ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
5. **Frontend** (tmux session `llmfront`): `cd frontend && npm install && NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev` → ready on :3000.
6. **Seed + verify**: `PYTHONPATH=$(pwd)/backend ./backend/venv/bin/python examples/demo.py` (needs backend up; logs events via SDK). Hit `/health`, POST `/api/events`, GET `/api/metrics/overview`, `/api/metrics/timeseries`, `/api/conversations`. Browser check with Playwright (`playwright install --with-deps chromium` in the backend venv): title `LLM Monitor Dashboard`, stats cards populated, console clean.

## Quirks discovered

- **init_db silently rolls back table creation on vanilla Postgres.** `backend/app/database.py` runs `CREATE EXTENSION timescaledb` in the same transaction as `create_all`; the failure poisons the transaction, so tables never materialize even though startup logs "Database initialized successfully". Symptom: endpoints 500 with `relation "llm_events" does not exist`. Fix at the source (split DDL from extension setup) or pre-create schema as above.
- **frontend/lib was gitignored** (Python `lib/` rule), so `@/lib/api` was absent and the dashboard 500'd with `Module not found`. Fixed on the onboarding branch: added `frontend/lib/api.ts` + `.gitignore` negations.
- **`/api/metrics/timeseries` GroupingError** — grouping by the parameterized `date_trunc` expression; asyncpg params prevent PostgreSQL from matching SELECT/GROUP BY expressions. Fixed by grouping on the `bucket` alias.
- Python 3.13 incompatibility with pinned deps (above); use 3.11.
- `npm run lint` prompts interactively (no ESLint config committed). Typecheck with `npx tsc --noEmit` works.

## Evidence (2026-09-24)

- `curl /health` → `{"status":"healthy"}`; 4 events POSTed (incl. one `error`), overview/timeseries/conversations all return data.
- `demo.py` SDK seed OK (gpt-4-mini etc. appear in dashboard).
- `npx tsc --noEmit` exit 0.
- Playwright headless screenshot: `/tmp/obvious-evidence/dashboard.png` (not persisted in snapshot artifacts); rendered text showed 7 requests, $0.02 cost, per-model breakdown, recent-calls table; console clean.
- Backend has no lint/typecheck/test suite; frontend lint unavailable without ESLint config.

## Backend: FastAPI (FastAPI-app pattern)

- Entry: `backend/app/main.py` — `lifespan` runs `init_db()`; routers: `/api/events`, `/api/metrics/*`, `/api/conversations`; health at `/` and `/health`.
- Run: `uvicorn app.main:app --host 0.0.0.0 --port 8000` from `backend/` with `DATABASE_URL` set.

## Frontend: Next.js dev server

- Run: `npm run dev` from `frontend/` with `NEXT_PUBLIC_API_URL` set. Port 3000 from startup output ("Ready" line). Dashboard polls data every 30s.
