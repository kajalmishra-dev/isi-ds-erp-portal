import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base
from app.models.tenant_mixin import TenantMixin


class Faculty(TenantMixin, Base):
    __tablename__ = "faculty"
    __table_args__ = (
        UniqueConstraint("tenant_id", "employee_code", name="uq_faculty_tenant_code"),
        UniqueConstraint("tenant_id", "email", name="uq_faculty_tenant_email"),
    )

    faculty_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    employee_code = Column(String(30), nullable=False, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20))
    email = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False, default="Computer Science & AI")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
