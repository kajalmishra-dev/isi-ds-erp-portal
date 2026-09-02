from uuid import UUID

from pydantic import BaseModel, Field


class MarksCreate(BaseModel):
    std_id: UUID
    exam_id: UUID
    sub_id: UUID
    marks_obtained: int = Field(ge=0)


class MarksResponse(BaseModel):
    mark_id: UUID
    std_id: UUID
    exam_id: UUID
    sub_id: UUID
    marks_obtained: int
    student_name: str | None = None
    enroll_no: str | None = None
    exam_name: str | None = None
    subject_name: str | None = None
    subject_code: str | None = None

    model_config = {"from_attributes": True}
