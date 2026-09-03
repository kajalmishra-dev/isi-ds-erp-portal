import uuid

from sqlalchemy import Column, Uuid


class TenantMixin:
    """Scopes every demo sandbox to its own tenant_id."""

    tenant_id = Column(Uuid(as_uuid=True), nullable=False, index=True)
