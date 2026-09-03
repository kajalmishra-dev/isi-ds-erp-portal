import uuid

from sqlalchemy import Column, DateTime, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base
from app.models.tenant_mixin import TenantMixin


class Subject(TenantMixin, Base):
    __tablename__ = "subjects"
    __table_args__ = (UniqueConstraint("tenant_id", "sub_code", name="uq_subjects_tenant_code"),)

    sub_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sub_code = Column(String(20), nullable=False)
    sub_name = Column(String(100), nullable=False)
    max_marks = Column(SmallInteger, nullable=False, default=100)
    semester = Column(SmallInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
