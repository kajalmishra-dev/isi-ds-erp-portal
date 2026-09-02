from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.ai import AskRequest, AskResponse
from app.services import ai_service

router = APIRouter(prefix="/api/ai", tags=["AI Assistant"])


@router.post("/ask", response_model=AskResponse)
def ask(
    payload: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ai_service.ask(db, current_user, payload.question)
