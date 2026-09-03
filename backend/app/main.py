from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

import app.tenant_context  # noqa: F401  # register SQLAlchemy tenant listeners
from app.config import settings
from app.database import Base, engine
from app.models import (  # noqa: F401
    Admin,
    Assignment,
    AttendanceRecord,
    AttendanceSession,
    CourseOffering,
    DemoTenant,
    Exam,
    Faculty,
    Mark,
    Notice,
    NoticeRead,
    PasswordResetToken,
    Student,
    Subject,
    Submission,
    User,
)
from app.routers import admin, ai, auth, faculty, notices, student
from app.seed import purge_stale_sandboxes, seed_demo_data


def _relax_user_designation_check() -> None:
    """Allow faculty on existing Postgres volumes that still have the old CHECK."""
    if not str(engine.url).startswith("postgresql"):
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_designation_check"))
    except Exception:
        pass


def _needs_schema_rebuild() -> bool:
    if settings.SEED_RESET:
        return True
    try:
        insp = inspect(engine)
        if not insp.has_table("users"):
            return False
        cols = {c["name"] for c in insp.get_columns("users")}
        return "tenant_id" not in cols
    except Exception:
        return True


async def _sandbox_gc_loop() -> None:
    while True:
        await asyncio.sleep(60 * 30)
        try:
            purge_stale_sandboxes()
        except Exception:
            pass


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if _needs_schema_rebuild():
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    _relax_user_designation_check()
    seed_demo_data()
    gc_task = asyncio.create_task(_sandbox_gc_loop())
    try:
        yield
    finally:
        gc_task.cancel()
        try:
            await gc_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title=settings.APP_NAME,
    version="2.6.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(faculty.router)
app.include_router(student.router)
app.include_router(notices.router)
app.include_router(ai.router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": "2.6.0",
        "demo_sandbox": settings.DEMO_SANDBOX,
        "sandbox_ttl_hours": settings.DEMO_TENANT_TTL_HOURS,
    }
