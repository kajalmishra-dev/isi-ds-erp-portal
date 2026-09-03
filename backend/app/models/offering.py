import uuid

from sqlalchemy import Column, DateTime, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.tenant_mixin import TenantMixin


class CourseOffering(TenantMixin, Base):
    __tablename__ = "course_offerings"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "sub_id", "academic_year", "term", name="uq_offering_tenant_subject_term"
        ),
    )

    offering_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sub_id = Column(
        UUID(as_uuid=True),
        ForeignKey("subjects.sub_id", ondelete="CASCADE"),
        nullable=False,
    )
    faculty_id = Column(
        UUID(as_uuid=True),
        ForeignKey("faculty.faculty_id", ondelete="CASCADE"),
        nullable=False,
    )
    academic_year = Column(SmallInteger, nullable=False)
    term = Column(String(20), nullable=False, default="Odd")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    subject = relationship("Subject")
    faculty = relationship("Faculty")
    sessions = relationship(
        "AttendanceSession",
        back_populates="offering",
        cascade="all, delete-orphan",
    )
