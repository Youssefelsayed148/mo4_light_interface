from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from app.db import get_session
from app.main import app


def test_health_reaches_postgres(client):
    for path in ("/health", "/api/health"):
        r = client.get(path)
        assert r.status_code == 200
        assert r.json() == {"status": "ok", "database": "ok"}


def test_health_returns_503_when_db_unreachable(client):
    bad = create_engine(
        "postgresql+psycopg://x:x@127.0.0.1:1/x",
        poolclass=NullPool,
        connect_args={"connect_timeout": 1},
    )

    def broken_session():
        with Session(bad) as s:
            yield s

    app.dependency_overrides[get_session] = broken_session
    try:
        r = client.get("/health")
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 503
    assert r.json()["detail"]["database"] == "unreachable"
