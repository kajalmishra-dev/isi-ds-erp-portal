import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.tenant_mixin import TenantMixin


class Assignment(TenantMixin, Base):
    __tablename__ = "assignments"

    assignment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    offering_id = Column(
        UUID(as_uuid=True),
        ForeignKey("course_offerings.offering_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(200), nullable=False)
    description = Column(Text)
    due_at = Column(DateTime(timezone=True), nullable=False)
    max_score = Column(Float, nullable=False, default=100.0)
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("faculty.faculty_id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    offering = relationship("CourseOffering")
    submissions = relationship(
        "Submission",
        back_populates="assignment",
        cascade="all, delete-orphan",
    )


class Submission(TenantMixin, Base):
    __tablename__ = "submissions"
    __table_args__ = (UniqueConstraint("assignment_id", "std_id", name="uq_submission_assignment_student"),)

    submission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assignments.assignment_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    std_id = Column(
        UUID(as_uuid=True),
        ForeignKey("students.std_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content = Column(Text, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    score = Column(Float)
    feedback = Column(Text)
    graded_at = Column(DateTime(timezone=True))
    graded_by = Column(
        UUID(as_uuid=True),
        ForeignKey("faculty.faculty_id", ondelete="SET NULL"),
        nullable=True,
    )

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("Student")
