"""Initial schema (SPEC section 2). org_id on every tenant table.

Airtable references are stored as IDs (tbl..., fld..., sel...), never names.
No attachment URLs are stored, only metadata (attachments_meta).
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def _pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def _org() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), ForeignKey("orgs.id", ondelete="CASCADE"), index=True)


def _fk(table: str, nullable: bool = False) -> Mapped[Any]:
    return mapped_column(UUID(as_uuid=True), ForeignKey(f"{table}.id"), nullable=nullable)


def _now() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), server_default=func.now())


class Org(Base):
    __tablename__ = "orgs"
    id: Mapped[uuid.UUID] = _pk()
    name: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = _now()


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("org_id", "key"),)
    id: Mapped[uuid.UUID] = _pk()
    org_id: Mapped[uuid.UUID] = _org()
    key: Mapped[str] = mapped_column(String(50))  # designer | video_editor
    label: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = _now()


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("org_id", "login"),)
    id: Mapped[uuid.UUID] = _pk()
    org_id: Mapped[uuid.UUID] = _org()
    login: Mapped[str] = mapped_column(String(200))
    name: Mapped[str] = mapped_column(String(200))
    password_hash: Mapped[str] = mapped_column(Text)  # argon2
    role_id: Mapped[uuid.UUID] = _fk("roles")
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))
    active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
    failed_logins: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = _now()


class AirtableAccount(Base):
    __tablename__ = "airtable_accounts"
    id: Mapped[uuid.UUID] = _pk()
    org_id: Mapped[uuid.UUID] = _org()
    role_id: Mapped[uuid.UUID] = _fk("roles")
    label: Mapped[str] = mapped_column(String(200))
    token_enc: Mapped[str] = mapped_column(Text)  # encrypted at rest
    created_at: Mapped[datetime] = _now()


class AirtableBase(Base):
    __tablename__ = "bases"
    __table_args__ = (UniqueConstraint("org_id", "airtable_base_id"),)
    id: Mapped[uuid.UUID] = _pk()
    org_id: Mapped[uuid.UUID] = _org()
    airtable_base_id: Mapped[str] = mapped_column(String(32))  # app...
    name: Mapped[str] = mapped_column(String(200))
    accent_index: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    created_at: Mapped[datetime] = _now()


class Binding(Base):
    __tablename__ = "bindings"
    __table_args__ = (
        UniqueConstraint("base_id", "role_id", "table_id"),
        CheckConstraint("sync_mode IN ('none','one_way','two_way')", name="ck_bindings_sync_mode"),
    )
    id: Mapped[uuid.UUID] = _pk()
    org_id: Mapped[uuid.UUID] = _org()
    base_id: Mapped[uuid.UUID] = _fk("bases")
    role_id: Mapped[uuid.UUID] = _fk("roles")
    airtable_account_id: Mapped[uuid.UUID] = _fk("airtable_accounts")
    table_id: Mapped[str] = mapped_column(String(32))  # tbl...
    title_field_id: Mapped[str] = mapped_column(String(32))  # fld...
    assignee_field_id: Mapped[str] = mapped_column(String(32))
    assignee_match: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    status_field_id: Mapped[str] = mapped_column(String(32))
    brief_field_ids: Mapped[list[str]] = mapped_column(JSONB, default=list)
    due_field_id: Mapped[str | None] = mapped_column(String(32))
    writable_fields: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)  # status/note/link
    sync_mode: Mapped[str] = mapped_column(String(10), default="none", server_default="none")
    active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
    created_at: Mapped[datetime] = _now()


class UserBinding(Base):
    __tablename__ = "user_bindings"
    __table_args__ = (UniqueConstraint("user_id", "binding_id"),)
    id: Mapped[uuid.UUID] = _pk()
    org_id: Mapped[uuid.UUID] = _org()
    user_id: Mapped[uuid.UUID] = _fk("users")
    binding_id: Mapped[uuid.UUID] = _fk("bindings")
    airtable_assignee_value: Mapped[str] = mapped_column(String(300))  # e.g. "Designer 1"
    created_at: Mapped[datetime] = _now()


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (UniqueConstraint("binding_id", "airtable_record_id"),)
    id: Mapped[uuid.UUID] = _pk()
    org_id: Mapped[uuid.UUID] = _org()
    binding_id: Mapped[uuid.UUID] = _fk("bindings")
    airtable_record_id: Mapped[str] = mapped_column(String(32), index=True)  # rec...
    title: Mapped[str] = mapped_column(Text)
    status: Mapped[str | None] = mapped_column(String(200))
    assignee_value: Mapped[str | None] = mapped_column(String(300), index=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    priority: Mapped[str | None] = mapped_column(String(100))
    brief: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    attachments_meta: Mapped[list[Any]] = mapped_column(JSONB, default=list)  # metadata, no URLs
    airtable_modified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))
    created_at: Mapped[datetime] = _now()


class ActivityLog(Base):
    __tablename__ = "activity_log"
    id: Mapped[uuid.UUID] = _pk()
    org_id: Mapped[uuid.UUID] = _org()
    user_id: Mapped[uuid.UUID | None] = _fk("users", nullable=True)
    task_id: Mapped[uuid.UUID | None] = _fk("tasks", nullable=True)
    field: Mapped[str] = mapped_column(String(100))
    old: Mapped[str | None] = mapped_column(Text)
    new: Mapped[str | None] = mapped_column(Text)
    result: Mapped[str] = mapped_column(String(50))  # ok | conflict | rejected | error
    at: Mapped[datetime] = _now()


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[uuid.UUID] = _pk()
    org_id: Mapped[uuid.UUID] = _org()
    user_id: Mapped[uuid.UUID] = _fk("users")
    task_id: Mapped[uuid.UUID | None] = _fk("tasks", nullable=True)
    kind: Mapped[str] = mapped_column(String(50))
    body: Mapped[str] = mapped_column(Text)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = _now()


class SyncState(Base):
    __tablename__ = "sync_state"
    id: Mapped[uuid.UUID] = _pk()
    org_id: Mapped[uuid.UUID] = _org()
    base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bases.id"), unique=True
    )
    webhook_id: Mapped[str | None] = mapped_column(String(64))
    mac_secret_enc: Mapped[str | None] = mapped_column(Text)  # shown once by Airtable; encrypted
    cursor: Mapped[int | None] = mapped_column(Integer)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_ok_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)


class ApiCallLog(Base):
    __tablename__ = "api_call_log"
    id: Mapped[uuid.UUID] = _pk()
    org_id: Mapped[uuid.UUID] = _org()
    base_id: Mapped[uuid.UUID | None] = _fk("bases", nullable=True)
    method: Mapped[str] = mapped_column(String(10))
    endpoint: Mapped[str] = mapped_column(String(300))
    status: Mapped[int | None] = mapped_column(Integer)
    at: Mapped[datetime] = _now()


class RateLimit(Base):
    __tablename__ = "rate_limit"
    __table_args__ = (UniqueConstraint("key", "window_start"),)
    id: Mapped[uuid.UUID] = _pk()
    org_id: Mapped[uuid.UUID] = _org()
    key: Mapped[str] = mapped_column(String(200))  # e.g. "airtable:app123" or "login:<login>"
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    count: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))


class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[uuid.UUID] = _pk()
    org_id: Mapped[uuid.UUID] = _org()
    user_id: Mapped[uuid.UUID] = _fk("users")
    token_hash: Mapped[str] = mapped_column(String(128), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = _now()
