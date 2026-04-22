import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Prefer DATABASE_URL env var (PostgreSQL in production).
# Fall back to local SQLite for development.
_env_url = os.getenv("DATABASE_URL", "")

if _env_url:
    DATABASE_URL = _env_url
    _engine_kwargs: dict = {}
else:
    DB_PATH = Path(__file__).parent / "kriyadocs.db"
    DATABASE_URL = f"sqlite:///{DB_PATH}"
    _engine_kwargs = {"connect_args": {"check_same_thread": False}}

engine = create_engine(DATABASE_URL, **_engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    from models import Customer, Session, UploadedFile, Rule, AuditLog  # noqa: F401
    Base.metadata.create_all(bind=engine)


def check_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
