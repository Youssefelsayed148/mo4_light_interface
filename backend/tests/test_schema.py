from sqlalchemy import inspect

from app.db import get_engine

EXPECTED = {
    "orgs",
    "users",
    "roles",
    "airtable_accounts",
    "bases",
    "bindings",
    "user_bindings",
    "tasks",
    "activity_log",
    "notifications",
    "sync_state",
    "api_call_log",
    "rate_limit",
    "sessions",
}


def test_all_spec_tables_exist_with_org_id():
    insp = inspect(get_engine())
    tables = set(insp.get_table_names())
    assert EXPECTED <= tables
    for t in EXPECTED - {"orgs"}:
        assert "org_id" in {c["name"] for c in insp.get_columns(t)}, t


def test_no_attachment_url_columns():
    insp = inspect(get_engine())
    cols = {c["name"] for c in insp.get_columns("tasks")}
    assert "attachments_meta" in cols
    assert not any("url" in c for c in cols)
