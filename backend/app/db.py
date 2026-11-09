from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.config import get_settings


@lru_cache
def get_engine() -> Engine:
    # NullPool: the backend is stateless (serverless); pooling is done by the
    # managed Postgres pooler in front of DATABASE_URL, not in this process.
    # prepare_threshold=None: no server-side prepared statements, which a
    # transaction-mode pooler (PgBouncer) cannot keep across connections.
    return create_engine(
        get_settings().database_url,
        poolclass=NullPool,
        pool_pre_ping=True,
        connect_args={"prepare_threshold": None},
    )


def get_session() -> Iterator[Session]:
    with sessionmaker(bind=get_engine(), expire_on_commit=False)() as session:
        yield session
