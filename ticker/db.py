from __future__ import annotations
from sqlmodel import SQLModel, create_engine, Session
from .config import CFG

# Create engine from environment
engine = create_engine(CFG.db_url, echo=False)

def init_db() -> None:
    """Initialize database schema."""
    from . import models  # ensures models are imported
    SQLModel.metadata.create_all(engine)

def get_session() -> Session:
    """Get a database session."""
    return Session(engine)
