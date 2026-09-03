from __future__ import annotations

import uuid
from contextvars import ContextVar

from sqlalchemy import event
from sqlalchemy.orm import Session, with_loader_criteria

from app.models.tenant_mixin import TenantMixin

current_tenant_id: ContextVar[uuid.UUID | None] = ContextVar("current_tenant_id", default=None)


def set_current_tenant(tenant_id: uuid.UUID | None) -> None:
    current_tenant_id.set(tenant_id)


def get_current_tenant() -> uuid.UUID | None:
    return current_tenant_id.get()


def _tenant_aware(obj: object) -> bool:
    return isinstance(obj, type) and issubclass(obj, TenantMixin) and hasattr(obj, "tenant_id")


@event.listens_for(Session, "do_orm_execute")
def _apply_tenant_filter(execute_state):
    tenant_id = current_tenant_id.get()
    if tenant_id is None or not execute_state.is_select:
        return
    execute_state.statement = execute_state.statement.options(
        with_loader_criteria(
            TenantMixin,
            lambda cls: cls.tenant_id == tenant_id,
            include_aliases=True,
        )
    )


@event.listens_for(Session, "before_flush")
def _stamp_tenant_on_flush(session, _flush_context, _instances):
    tenant_id = current_tenant_id.get()
    if tenant_id is None:
        return
    for obj in session.new:
        if isinstance(obj, TenantMixin):
            obj.tenant_id = tenant_id
