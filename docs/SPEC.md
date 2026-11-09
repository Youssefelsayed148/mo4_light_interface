# SPEC - Light Interface

## 1. Roles and bindings
- Role (global): designer, video_editor. Same capabilities in every base: view my tasks, set status, add note, add link.
- Airtable account (per role): one company-owned integration account per role (Designer account, Video Editor account). Token stored encrypted. Nobody logs into Airtable with it. Airtable field permissions keep each account out of the other role's fields (confirm the option on the plan in the sandbox).
- Binding (per base + role): base_id, airtable_account, table_id, title_field, assignee_field + match rule, status_field, brief_fields[], due_field, writable_fields[] (status, note, link), sync_mode (none | one_way | two_way).
- Person-to-Airtable mapping (user_bindings), e.g. Designer 1. Platform login is always per person, never shared.
- Status changes are not strictly ordered: any option of the status field is allowed, and options are read from the Airtable schema.
- A new base is a new binding row, not new code. A binding health check flags renamed or deleted fields.

## 2. Data model (Postgres, org_id on every table)
orgs, users (argon2 hash, role, is_admin, active), roles, airtable_accounts, bases, bindings, user_bindings,
tasks (normalized: title, status, assignee_value, due_at, priority, brief jsonb, attachments_meta jsonb, airtable_record_id, airtable_modified_at, deleted),
activity_log (user, task, field, old, new, result, at), notifications,
sync_state (webhook_id, mac_secret_enc, cursor, expires_at, last_ok_at, last_error),
api_call_log, rate_limit, sessions. Later: must_change_password flag.

## 3. API
- Auth: POST /auth/login, /auth/logout, /auth/change-password; GET /me
- Tasks: GET /tasks (mine, base, status, due); GET /tasks/{id}; POST /tasks/{id}/status {value, expected_current}; POST /tasks/{id}/note; POST /tasks/{id}/link; GET /tasks/{id}/files/{att_id}
- Notifications: GET /notifications; POST /notifications/{id}/read
- Admin: users CRUD + password reset, bases, bindings, GET /admin/health (sync, API usage vs quota, binding health)
- Sync: POST /hooks/airtable/{base_id} (verify MAC); POST /cron/refresh; POST /cron/reconcile (protected by CRON_SECRET)

## 4. Sync (stateless, idempotent)
- First load: list records (100 per page), upsert tasks, register webhook with notificationUrl, store the MAC secret encrypted (it is shown once).
- Ping: verify X-Airtable-Content-MAC, answer 200/204 fast, list payloads from the stored cursor (page while mightHaveMore), upsert, save the cursor.
- Daily cron: refresh the webhook (it expires after 7 days; listing payloads also extends it), then a full reconcile to catch misses and deletes (mark deleted).
- Refresh on open: if a base's last_ok_at is stale, run a rate-limited reconcile.
- Hobby plan: daily cron only. Pro plan: optional 5-minute backup reconcile.
- Synced tables: sync_mode per table. Test in the sandbox whether destination webhooks fire for source-side edits; the reconcile covers any gap.

## 5. Write-back
Allowed: status, note, link only, on the person's own tasks.
Steps: check role + ownership + whitelisted field -> read the current record (1 call) -> if status differs from expected_current return 409 with the latest -> write with the role account token -> update mirror -> activity_log -> notify.
Never write synced fields unless sync_mode is two_way and the field is editable.

## 6. UI
- Screens: Login, My Tasks (combined across bases, base chips, filters), Task detail (brief, source link, status control, note, link, history), Notifications badge + list, Role dashboard, Admin (users, bindings, health).
- Dynamic: columns and detail fields come from the binding, status options from the schema, one accent color per base.
- Designer / Video Editor dashboard: my tasks by status, due soon, done this week.
- Manager dashboard: workload per person, overdue, stuck, sync health, API usage with warnings at 70% and 90%.

## 7. Theme tokens (CSS variables)
- Dark (default): bg #17171a, surface #1f1f23, border #2c2c31, text #ececef, muted #9a9aa3.
- Light grey: bg #f2f2f4, surface #ffffff, border #dcdce1, text #1a1a1f, muted #6b6b75.
- Switcher: system / light / dark.
- Status colors: unassigned grey, assigned blue, in progress amber, ready/done green, overdue/failed rose.
- Base accents: indigo, teal, violet, amber (cycle).
- Inter font, 12px radius, subtle motion only.
