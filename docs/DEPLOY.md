# Deploy runbook (Phase 1: health endpoint on Vercel + managed Postgres)

Do this only after the app runs locally (it does). Nothing here uses Airtable or real tokens.

## 1. Database (recommended: Neon, pooled)

Why: Postgres with a built-in PgBouncer pooler, which the stateless Vercel backend needs, and a Vercel Marketplace integration.
Alternative: Supabase (use the transaction pooler string). Everything below applies the same way.

1. Create a Neon project (Vercel Marketplace: Storage > Neon, or neon.com). Region close to the Vercel function region.
2. Get **two** connection strings:
   - **Pooled** (host contains `-pooler`): used by the running backend as `DATABASE_URL`.
   - **Direct** (no `-pooler`): used only to run migrations from your machine.
3. Keep `sslmode=require` on both. The backend rewrites `postgres://` / `postgresql://` to the psycopg3 driver itself, so paste the URL as the provider gives it.
4. The backend already disables prepared statements (`prepare_threshold=None`) and uses no in-process pool, which is what a transaction-mode pooler needs.

If you use the Neon integration inside Vercel it injects `DATABASE_URL` and `DATABASE_URL_UNPOOLED`.
Check in Project Settings > Environment Variables that `DATABASE_URL` really contains `-pooler`.

## 2. Run the migration (once, from your machine, against the DIRECT url)

PowerShell:
```
cd backend
$env:DATABASE_URL = "<DIRECT connection string>"
.venv\Scripts\alembic upgrade head
.venv\Scripts\alembic current        # expect: 0001 (head)
Remove-Item Env:DATABASE_URL
```
Environment variables override the local `.env`, so your local DB is untouched. Do not commit the string.

## 3. Secrets (generate fresh values, never reuse the local ones)

```
python -c "import secrets; print(secrets.token_urlsafe(48))"                       # SESSION_SECRET
python -c "import secrets; print(secrets.token_urlsafe(48))"                       # CRON_SECRET
python -c "import base64,os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"  # TOKEN_ENCRYPTION_KEY (Fernet-compatible, used from Phase 2)
```
Store them only in a password manager and in Vercel. Losing `TOKEN_ENCRYPTION_KEY` later means re-entering the encrypted Airtable tokens.

## 4. Vercel project

1. Import the GitHub repo. **Root Directory: repository root** (not `frontend/`), because `vercel.json` is at the root and defines both services.
2. If Vercel does not detect the services setup by itself, set Settings > Build > Framework Preset to **Services**.
3. Environment Variables (Production, and Preview if you want preview deploys to work):

   | Name | Value |
   |---|---|
   | `DATABASE_URL` | pooled connection string |
   | `SESSION_SECRET` | generated |
   | `TOKEN_ENCRYPTION_KEY` | generated |
   | `CRON_SECRET` | generated |

   Mark them Sensitive. Do not add Airtable tokens (not needed in this phase).
4. Deploy.

## 5. Verify

- `https://<project>.vercel.app/` shows the landing page (both themes work).
- `https://<project>.vercel.app/api/health` returns `{"status":"ok","database":"ok"}`.
- A wrong or unreachable `DATABASE_URL` returns HTTP 503 with `{"detail":{"status":"error","database":"unreachable"}}`.
- Vercel > Deployments > Runtime Logs show no errors.

## Known uncertainties (check at first deploy)

- Vercel Services is Beta. The docs show `"entrypoint": "Dockerfile"` for container services; a custom name (`Dockerfile.vercel`, as used in a Vercel Labs example) is **not confirmed**. If the build rejects it: rename `backend/Dockerfile.vercel` to `backend/Dockerfile`, set `"entrypoint": "Dockerfile"` in `vercel.json`, and update AGENTS.md.
- The container must listen on `$PORT`; the Dockerfile does that (default 8000 locally).
- Vercel keeps the `/api` prefix; the backend serves `/api/health` (and `/health` for local use).

## Rollback
Vercel > Deployments > previous deployment > Promote to Production. The schema migration is additive (`alembic downgrade base` only on an empty database).
