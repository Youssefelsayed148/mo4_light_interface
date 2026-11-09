# STATE - Light Interface
Last updated: 2026-11-09 (Phase 1 done locally; deploy pending)

## Decisions (locked)
- Internal MO4 tool; org_id kept for a possible product later.
- Login: admin-created accounts in Postgres; users change their own password in the app. Google sign-in later.
- Global roles (Designer, Video Editor) bound per base. Permissions per table + row (my tasks) + field whitelist. Status order not strict.
- Two company-owned Airtable integration accounts (one per role); per-person platform logins.
- GitHub -> Vercel (frontend + FastAPI container), managed Postgres with pooling. Stateless sync (webhooks + cron).
- In-app badge notifications. Charcoal / light grey theme with accent colors.
- Sandbox: the "Agency (Youssef)" copy.

## Phase 0 - Your prep (not Claude Code)
- [ ] Check Airtable plan (Workspace > Billing) and that field permissions are available
- [ ] Email Airtable: internal app, staff without seats update status through two role integration accounts - is that compliant?
- [ ] Create the two integration accounts and sandbox tokens (minimum scopes, sandbox base only)
- [ ] Managed Postgres, GitHub repo, Vercel project; decide Hobby vs Pro
- [ ] First user list: name, login, role, Airtable value

## Phases (done when ...)
- [x] 1 Foundation (local part done; deploy pending): repo, Dockerfile.vercel, schema + migrations; health endpoint live on Vercel and reaching Postgres
  - [x] Repo layout, git init, CLAUDE.md, .gitignore, .env.example
  - [x] Backend: FastAPI, SQLAlchemy 2 models (14 tables), Alembic 0001 (upgrade/downgrade verified), GET /health + /api/health checks DB
  - [x] backend/Dockerfile.vercel builds and answers /health and /api/health against local Postgres
  - [x] docker-compose local Postgres (port 5433), pytest (4 pass), ruff clean
  - [x] Frontend: Vite + React + TS, tokens as CSS variables, system/light/dark switcher, landing page, vitest (4 pass), build + lint clean
  - [x] Tailwind blocker resolved by running the frontend in Docker (compose service `frontend`, Linux node_modules volume). Landing page checked in the browser in light and dark.
  - [x] Deploy prep done: docs/DEPLOY.md runbook, driver set for a transaction pooler (prepare_threshold=None), container listens on $PORT, local DB password changed to a testing value
  - [ ] PENDING (last step): you create the Vercel project + managed Postgres (Neon recommended) and give me the project URL; then follow docs/DEPLOY.md (migrate with the direct URL, set 4 env vars, deploy, check /api/health)
  - [ ] PENDING: confirm Vercel accepts `entrypoint: "Dockerfile.vercel"` (fallback in docs/DEPLOY.md)
- [ ] 2 Auth + admin: admin creates a designer; the designer logs in and changes the password
- [ ] 3 Roles + bindings: sandbox schema audit (which tables are synced, assignee field type); Designer binding resolves real field IDs
- [ ] 4 Sync: first load, webhook, cursor, deletes, daily refresh, call counter + limiter; an Airtable edit shows in the mirror within seconds
- [ ] 5 Write-back: status/note/link writes, conflict check, activity log; a status change fires the existing Airtable automation
- [ ] 6 UI: dynamic My Tasks + detail, themes, notifications; a designer completes a task in a few clicks
- [ ] 7 Dashboards: role dashboards + manager view (workload, overdue, sync health, API usage)
- [ ] 8 Pilot: one designer + one video editor, then a real base; measure seats saved

## Sandbox tests (record results here)
- [ ] API write to a two-way synced field
- [ ] Do source-side edits appear in destination webhook payloads?
- [ ] Field permissions: can the Designer account be kept out of video fields?
- [ ] Attachment URL refresh through the API

## Findings
- 2026-11-09: A Windows Application Control policy blocks `@tailwindcss/oxide-win32-x64-msvc` (`tailwindcss-oxide.win32-x64-msvc.node`: "An Application Control policy has blocked this file"). Tailwind falls back to the WASI build, whose scanner sees 0 files, so no utilities are emitted (build CSS 7.6 kB, no .flex/.bg-surface). Not a code bug; Linux builds on Vercel are unaffected.
- Resolution: frontend dev/build/test run in the `frontend` compose service (node:22, Linux binary loads; CSS 13.9 kB with utilities). Host `npm test` and `npm run lint` still work (vitest does not need the native binary).
- Port 8000 is used by another local project (mo4table-api); this app uses 8010 (backend) and 5173 (frontend), Postgres on 5433.
- Vercel keeps the /api prefix, so the backend serves both /health and /api/health.

## Open items
- Airtable terms/seat answer (in writing)
- Airtable plan (Team 100k calls/month, Business unlimited)
- Vercel plan (Hobby cron daily only, Pro per minute)
- Assignee field type in the Agency base (collaborator vs select)

## Later
Forced password change at first login, Google sign-in, Drive upload, email notifications, Instagram + insights, more roles, n8n workflow health.

## Session log
- 2026-11-09: Deploy runbook written; waiting for the Vercel project URL and DATABASE_URL.
- 2026-11-09: Phase 1 verified locally (backend tests, migrations, container health, styled landing page in both themes). Tailwind blocker solved via Docker. Only deployment is left. 
