from app.database_config import SessionLocal


def get_db():
    """
    FastAPI dependency that provides a database session to routes.
    Opens a session, yields it, and ensures it's closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
