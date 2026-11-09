# MO4 Light Interface

Internal web app for light Airtable users (Designers, Video Editors): see my tasks, change a status, add a note or link. Airtable stays the source of truth. See [docs/SPEC.md](docs/SPEC.md) and [STATE.md](STATE.md).

```
frontend/   React + TypeScript + Vite + Tailwind v4 + shadcn/ui
backend/    FastAPI + SQLAlchemy 2 + Alembic (Dockerfile.vercel for deploy)
docker-compose.yml   local Postgres (development only)
vercel.json          two services: frontend + backend container (not deployed yet)
```

## Prerequisites
Python 3.12, Node 22+, Docker (for local Postgres).

## Local run

1. **Env file.** Copy `.env.example` to `.env` and fill the values. For local dev:
   ```
   DATABASE_URL=postgresql+psycopg://mo4:mo4databasepw1@localhost:5433/mo4
   SESSION_SECRET=any-local-value
   TOKEN_ENCRYPTION_KEY=any-local-value
   CRON_SECRET=any-local-value
   ```
2. **Postgres** (port 5433 so it does not clash with other local databases):
   ```
   docker compose up -d
   ```
3. **Backend** (port 8010):
   ```
   cd backend
   py -3.12 -m venv .venv            # macOS/Linux: python3.12 -m venv .venv
   .venv/Scripts/pip install -e ".[dev]"   # macOS/Linux: .venv/bin/pip
   .venv/Scripts/alembic upgrade head
   .venv/Scripts/uvicorn app.main:app --port 8010 --reload
   ```
   Check: <http://localhost:8010/health> returns `{"status":"ok","database":"ok"}`
   (also served at `/api/health`, the path Vercel will route to the backend).
4. **Frontend** (port 5173, proxies `/api` to the backend on 8010). It runs in Docker with its own
   Linux `node_modules` volume, because Tailwind v4's native binary is blocked by Windows
   Application Control on some machines:
   ```
   docker compose up frontend
   ```
   On a machine where the native binary loads you can also run `npm install && npm run dev`
   inside `frontend/`.

## Quality checks
```
cd backend  && .venv/Scripts/ruff check . && .venv/Scripts/ruff format --check . && .venv/Scripts/python -m pytest
docker compose run --rm frontend sh -c "npm install && npm run lint && npm test && npm run build"
```
Backend tests run the real Alembic migrations against the local Postgres (`DATABASE_URL`), so `docker compose up -d` must be running.

## Migrations
```
cd backend
.venv/Scripts/alembic revision --autogenerate -m "describe change"
.venv/Scripts/alembic upgrade head
```
Review every generated migration before applying it.

## Deployment
Not set up yet (Phase 1 is local only). It needs a managed Postgres `DATABASE_URL` and a Vercel project; see the pending steps in [STATE.md](STATE.md).
