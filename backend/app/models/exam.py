import uuid

from sqlalchemy import Boolean, Column, DateTime, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class Exam(Base):
    __tablename__ = "exams"
    __table_args__ = (UniqueConstraint("exam_name", "year", "semester"),)

    exam_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_name = Column(String(100), nullable=False)
    year = Column(SmallInteger, nullable=False)
    semester = Column(SmallInteger)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
