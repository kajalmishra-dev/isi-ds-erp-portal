import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Notice(Base):
    __tablename__ = "notices"

    notice_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    audience = Column(String(20), nullable=False, default="all")  # all|admin|faculty|student|offering
    offering_id = Column(
        UUID(as_uuid=True),
        ForeignKey("course_offerings.offering_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
    )
    is_active = Column(Boolean, nullable=False, default=True)
    published_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    offering = relationship("CourseOffering")
    author = relationship("User")
    reads = relationship("NoticeRead", back_populates="notice", cascade="all, delete-orphan")


class NoticeRead(Base):
    __tablename__ = "notice_reads"
    __table_args__ = (UniqueConstraint("notice_id", "user_id", name="uq_notice_read_user"),)

    read_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notice_id = Column(
        UUID(as_uuid=True),
        ForeignKey("notices.notice_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    read_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    notice = relationship("Notice", back_populates="reads")
