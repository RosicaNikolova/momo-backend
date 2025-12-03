from typing import List

from sqlalchemy.orm import Session

from app.repository import resident_repository
from app.schemas.resident import ResidentRead

DEFAULT_OFFSET = 0
MAX_LIMIT = 500
MIN_LIMIT = 1
DEFAULT_LIMIT = 50


def get_residents(
    db: Session, offset: int = DEFAULT_OFFSET, limit: int = DEFAULT_LIMIT
) -> List[ResidentRead]:

    # Sanitize pagination parameters (defensive). Router also validates via Query.
    offset = max(DEFAULT_OFFSET, int(offset))
    limit = max(MIN_LIMIT, min(int(limit), MAX_LIMIT))

    orm_residents = resident_repository.get_residents(db, offset=offset, limit=limit)

    # Convert ORM -> Pydantic DTOs (Pydantic v2)
    return [ResidentRead.model_validate(r) for r in orm_residents]


def get_resident(db: Session, resident_id: int) -> ResidentRead | None:
    """Return a ResidentRead DTO for given id, or None if not found.

    Service returns None when the resident doesn't exist so the router can
    translate that into a 404 HTTP response.
    """
    orm_res = resident_repository.get_resident(db, resident_id)
    if orm_res is None:
        return None
    return ResidentRead.model_validate(orm_res)
