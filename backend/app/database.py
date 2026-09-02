from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine_kwargs: dict = {"pool_pre_ping": True}
connect_args: dict = {}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
