from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class NoticeCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    body: str = Field(min_length=2, max_length=8000)
    audience: str = Field(pattern="^(all|admin|faculty|student|offering)$")
    offering_id: UUID | None = None

    @model_validator(mode="after")
    def offering_required_for_course(self):
        if self.audience == "offering" and not self.offering_id:
            raise ValueError("offering_id is required when audience is offering")
        if self.audience != "offering":
            self.offering_id = None
        return self


class NoticeOut(BaseModel):
    notice_id: UUID
    title: str
    body: str
    audience: str
    offering_id: UUID | None = None
    offering_label: str | None = None
    author_name: str | None = None
    author_role: str | None = None
    published_at: datetime
    is_read: bool = False


class NoticeListResponse(BaseModel):
    notices: list[NoticeOut]
    unread_count: int
