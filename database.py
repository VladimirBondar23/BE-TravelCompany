"""
Database engine, session, and lifecycle.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL
from models import Base

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency that yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create tables and run migrations (e.g. add optional columns)."""
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE project_places ADD COLUMN title VARCHAR(500)"))
            conn.commit()
    except Exception:
        pass
