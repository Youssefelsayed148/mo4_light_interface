# AGENTS.md - Light Interface (MO4 internal tool)

Read STATE.md and docs/SPEC.md at the start of every session. Update STATE.md at the end.

## Purpose
An external web app for light Airtable users (Designers, Video Editors): see my tasks, change a status, add a note or link. Airtable stays the source of truth, and existing Airtable automations must keep firing.

## Stack
- Frontend: React + TypeScript + Tailwind + shadcn/ui (Vite).
- Backend: FastAPI (Python 3.12), SQLAlchemy 2, Alembic, httpx.
- Database: managed Postgres through a pooled connection string.
- Hosting: GitHub -> Vercel. Frontend and a FastAPI container (Dockerfile.vercel) as two services in one project. Check Vercel's current container-image docs before writing config.
- Quality: pytest, vitest, ruff. Run them before saying a step is done.

## Hard rules
1. One phase at a time. Stop at the phase's "done when", report, and wait for "go on".
2. Sandbox only: never use a live base or a live token. Tokens and base IDs come from env vars. Never commit secrets; keep .env.example with names only.
3. Ask before: schema or migration changes, new dependencies, deleting files, auth changes, any Airtable write outside the whitelist.
4. Permissions are enforced in the backend only. Never trust the UI.
5. Every Airtable write goes through one write-back service: whitelist check, compare-before-write, Airtable call, mirror update, activity_log entry.
6. Bindings store Airtable IDs (tbl..., fld..., sel...), never names.
7. Never store or cache attachment URLs (they expire in about 2 hours). Store metadata and fetch a fresh URL on demand.
8. The backend is stateless (Vercel functions): no background loops, no in-memory state between requests. Cursors, rate-limit counters and sessions live in Postgres.
9. Airtable limits: at most 3 requests per second per base, back off 30 seconds after a 429, batch writes (10 records per request), log every call in api_call_log.
10. Do not guess Airtable behaviour. If unsure (synced-table writes, webhooks on synced tables), write a sandbox test, run it, and record the result in STATE.md.
11. Passwords: argon2, lockout after repeated failures, httpOnly cookie sessions, no signup route, tokens encrypted at rest.
12. UI: design tokens only (CSS variables), no hard-coded colors, mobile-first, keyboard accessible, readable contrast in both themes.
13. Keep it simple: no features outside the current phase, and prefer fewer moving parts.

## Working loop
Plan the step in 3-5 lines -> implement -> test -> lint -> update STATE.md -> short report (what changed, how it was verified, what is next).

## Corrections log
When the user corrects you: restate the rule in one line, add it here, and follow it from then on.
- (none yet)
