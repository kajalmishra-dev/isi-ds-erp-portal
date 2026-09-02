import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.notice import NoticeListResponse
from app.services import notice_service

router = APIRouter(prefix="/api/notices", tags=["Notices"])


@router.get("", response_model=NoticeListResponse)
def list_notices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return notice_service.list_notices(db, current_user)


@router.post("/{notice_id}/read", response_model=MessageResponse)
def mark_read(
    notice_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return notice_service.mark_notice_read(db, current_user, notice_id)
