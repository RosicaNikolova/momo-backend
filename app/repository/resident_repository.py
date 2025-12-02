from typing import List
from sqlalchemy.orm import Session

# Import the ORM model for residents
from app.orm_models.resident import Resident


def get_residents(db: Session, offset: int = 0, limit: int = 50) -> List[Resident]:
    """Return a list of Resident ORM objects.


    Parameters
    - db: SQLAlchemy Session (injected by dependency)
    - offset: number of rows to skip (for pagination)
    - limit: maximum number of rows to return

    Returns a list (possibly empty) of Resident instances.
    """
    return (
        db.query(Resident)
        .order_by(Resident.id)
        .offset(max(0, offset))
        .limit(max(1, limit))
        .all()
    )


def get_resident(db: Session, resident_id: int) -> Resident | None:
    """Return a single Resident ORM instance or None if not found."""
    return db.query(Resident).filter(Resident.id == int(resident_id)).first()
