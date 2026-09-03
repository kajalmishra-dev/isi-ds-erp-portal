import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.tenant_mixin import TenantMixin


class AttendanceSession(TenantMixin, Base):
    __tablename__ = "attendance_sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    offering_id = Column(
        UUID(as_uuid=True),
        ForeignKey("course_offerings.offering_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_date = Column(Date, nullable=False)
    topic = Column(String(200))
    taken_by = Column(
        UUID(as_uuid=True),
        ForeignKey("faculty.faculty_id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    offering = relationship("CourseOffering", back_populates="sessions")
    records = relationship(
        "AttendanceRecord",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class AttendanceRecord(TenantMixin, Base):
    __tablename__ = "attendance_records"
    __table_args__ = (UniqueConstraint("session_id", "std_id", name="uq_attendance_session_student"),)

    record_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("attendance_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    std_id = Column(
        UUID(as_uuid=True),
        ForeignKey("students.std_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(String(20), nullable=False, default="present")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session = relationship("AttendanceSession", back_populates="records")
    student = relationship("Student")
