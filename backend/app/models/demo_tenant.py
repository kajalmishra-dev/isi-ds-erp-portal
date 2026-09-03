import uuid

from sqlalchemy import Column, DateTime, String, Uuid
from sqlalchemy.sql import func

from app.database import Base


class DemoTenant(Base):
    """One private sandbox world for a visitor."""

    __tablename__ = "demo_tenants"

    tenant_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label = Column(String(80), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_seen_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
