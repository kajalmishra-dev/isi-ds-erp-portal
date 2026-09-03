from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config import settings
from app.dependencies import get_db
from app.models.demo_tenant import DemoTenant
from app.models.user import User
from app.schemas.auth import (
    DemoStartRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginResponse,
    MessageResponse,
    ResetPasswordRequest,
)
from app.seed import create_visitor_sandbox
from app.services import auth_service
from app.tenant_context import set_current_tenant
from app.utils.jwt_handler import create_access_token
from app.utils.ids import as_uuid

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

ROLE_USERNAME = {
    "admin": "admin",
    "faculty": "faculty",
    "student": "student",
}


@router.post("/login", response_model=LoginResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    if settings.DEMO_SANDBOX:
        raise HTTPException(
            status_code=400,
            detail="Use demo sign-in on the home page. Each visitor gets a private sandbox.",
        )

    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        {
            "sub": str(user.user_id),
            "role": user.designation,
            "tenant_id": str(user.tenant_id),
        }
    )
    return LoginResponse(
        access_token=token,
        role=user.designation,
        username=user.username,
        tenant_id=str(user.tenant_id),
        sandbox=False,
    )


@router.post("/demo-start", response_model=LoginResponse)
def demo_start(payload: DemoStartRequest, db: Session = Depends(get_db)):
    """Create or reuse a private sandbox, then sign in as the chosen demo role."""
    role = payload.role
    username = ROLE_USERNAME[role]

    tenant_id = None
    if payload.tenant_id:
        try:
            tenant_id = as_uuid(payload.tenant_id)
        except HTTPException:
            tenant_id = None
        if tenant_id is not None:
            exists = db.query(DemoTenant).filter(DemoTenant.tenant_id == tenant_id).first()
            if not exists:
                tenant_id = None

    if tenant_id is None:
        if not settings.DEMO_SANDBOX:
            # Single shared world: seed master if needed, then login role
            from app.seed import seed_demo_data
            import uuid as uuid_mod

            master = uuid_mod.UUID(settings.MASTER_TENANT_ID)
            seed_demo_data(tenant_id=master, db=db)
            tenant_id = master
        else:
            tenant_id = create_visitor_sandbox(db)

    set_current_tenant(tenant_id)
    try:
        user = (
            db.query(User)
            .filter(
                User.tenant_id == tenant_id,
                User.username == username,
                User.is_active.is_(True),
            )
            .first()
        )
    finally:
        set_current_tenant(None)

    if not user:
        raise HTTPException(status_code=500, detail="Demo user missing in sandbox")

    # Touch tenant activity so GC keeps active sandboxes
    from datetime import datetime, timezone

    db.query(DemoTenant).filter(DemoTenant.tenant_id == tenant_id).update(
        {"last_seen_at": datetime.now(timezone.utc)},
        synchronize_session=False,
    )
    db.commit()

    token = create_access_token(
        {
            "sub": str(user.user_id),
            "role": user.designation,
            "tenant_id": str(tenant_id),
        }
    )
    return LoginResponse(
        access_token=token,
        role=user.designation,
        username=user.username,
        tenant_id=str(tenant_id),
        sandbox=settings.DEMO_SANDBOX,
    )


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return auth_service.request_password_reset(
        db,
        username=payload.username,
        enroll_no=payload.enroll_no,
        email=str(payload.email) if payload.email else None,
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    return auth_service.reset_password(
        db,
        username=payload.username,
        reset_code=payload.reset_code,
        new_password=payload.new_password,
    )
