import uuid

from sqlalchemy import Column, DateTime, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class Subject(Base):
    __tablename__ = "subjects"

    sub_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sub_code = Column(String(20), unique=True, nullable=False)
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
