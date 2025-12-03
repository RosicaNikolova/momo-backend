import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./momo.db")

# SQLite needs this argument for FastAPI’s multi-threaded dev server
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Create engine = “connection manager” to your DB
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# SessionLocal gives each request its own DB session
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# Base class: all your model classes will inherit from this
class Base(DeclarativeBase):
    pass
