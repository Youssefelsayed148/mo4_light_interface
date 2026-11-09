import pytest
from alembic.config import Config
from fastapi.testclient import TestClient

from alembic import command
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def migrated_db():
    """Run the real migrations against the local Postgres before tests."""
    command.upgrade(Config("alembic.ini"), "head")


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
