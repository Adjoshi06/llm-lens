# Codebase Map

| Path | What it is | Key files |
|---|---|---|
| `backend/` | FastAPI API server (Python 3.11, pip/venv) | `app/main.py` (app factory, lifespan, health), `requirements.txt`, `Dockerfile` |
| `backend/app/` | Core app: DB engine, models, Pydantic schemas | `database.py` (engine, `init_db`), `models.py` (`LLMEvent`), `schemas.py` |
| `backend/app/routers/` | API routes under `/api` | `events.py` (POST/GET events), `metrics.py` (overview, timeseries), `conversations.py` |
| `backend/app/monitor/` | Python SDK + model pricing | `sdk.py` (`LLMMonitor` decorator), `pricing.py` (per-model token costs) |
| `frontend/` | Next.js 14 App Router dashboard (npm) | `package.json`, `next.config.js`, `tsconfig.json`, `Dockerfile` |
| `frontend/app/` | Pages and global styles | `page.tsx` (dashboard, 30s auto-refresh), `layout.tsx` |
| `frontend/components/` | Dashboard UI pieces | `StatsCard.tsx`, `MetricsChart.tsx` (Recharts lines), `CostTracker.tsx` (pie), `RecentCalls.tsx` (table) |
| `frontend/lib/` | Shared frontend code | `api.ts` (axios client, types — restored after being gitignored) |
| `examples/` | SDK usage demo / seed script | `demo.py` (logs success + error events via SDK) |
| root | Ops + docs | `docker-compose.yml` (db/backend/frontend), `setup.sh` / `setup.ps1`, `README.md`, `QUICKSTART.md` |
