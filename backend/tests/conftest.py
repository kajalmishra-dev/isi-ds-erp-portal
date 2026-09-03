import uuid

import bcrypt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 — register all tables on Base.metadata
from app.config import settings
from app.database import Base
from app.dependencies import get_db
from app.main import app
from app.models.demo_tenant import DemoTenant
from app.models.faculty import Faculty
from app.models.user import User

MASTER = uuid.UUID(settings.MASTER_TENANT_ID)

engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr("app.main.engine", engine)
    monkeypatch.setattr("app.main.seed_demo_data", lambda: None)
    monkeypatch.setattr("app.main._relax_user_designation_check", lambda: None)
    monkeypatch.setattr("app.main._needs_schema_rebuild", lambda: False)
    monkeypatch.setattr(settings, "DEMO_SANDBOX", False)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(DemoTenant(tenant_id=MASTER, label="test-master"))
    admin = User(
        tenant_id=MASTER,
        username="admin",
        password=bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode(),
        designation="admin",
    )
    faculty_user = User(
        tenant_id=MASTER,
        username="faculty",
        password=bcrypt.hashpw(b"faculty123", bcrypt.gensalt()).decode(),
        designation="faculty",
    )
    db.add(admin)
    db.add(faculty_user)
    db.flush()
    db.add(
        Faculty(
            tenant_id=MASTER,
            user_id=faculty_user.user_id,
            employee_code="FAC-01",
            first_name="Arjun",
            last_name="Nair",
            email="arjun@isi-ds.edu",
            department="Data Science",
        )
    )
    db.commit()
    db.close()

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
