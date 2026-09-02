from uuid import UUID

from pydantic import BaseModel, Field


class ExamCreate(BaseModel):
    exam_name: str = Field(min_length=2, max_length=100)
    year: int = Field(ge=2000, le=2100)
    semester: int = Field(ge=1, le=12)
    is_active: bool = True


class ExamResponse(BaseModel):
    exam_id: UUID
    exam_name: str
    year: int
    semester: int | None = None
    is_active: bool

    model_config = {"from_attributes": True}
