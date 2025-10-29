from typing import List
from fastapi import APIRouter, Depends, Query
from app.dependencies import get_db
from sqlalchemy.orm import Session
from app.schemas.resident import ResidentRead
from app.services import residents_service
from fastapi import HTTPException

router = APIRouter(prefix="/api/residents", tags=["Residents"])

# Pagination defaults / caps (use constants so values are easy to change)
DEFAULT_OFFSET = 0
DEFAULT_LIMIT = 50
MAX_LIMIT = 500
MIN_LIMIT = 1


@router.get("/", response_model=List[ResidentRead])
def get_residents(
    db: Session = Depends(get_db),
    offset: int = Query(DEFAULT_OFFSET, ge=0,
                        description="Number of rows to skip"),
    limit: int = Query(DEFAULT_LIMIT, ge=MIN_LIMIT, le=MAX_LIMIT,
                       description=f"Max rows to return (capped at {MAX_LIMIT})"),
) -> List[ResidentRead]:
    """List residents with simple pagination.

    Query parameters:
    - offset: skip this many rows, used for pagination
    - limit: max number of rows to return

    """
    return residents_service.get_residents(db, offset=offset, limit=limit)


@router.get("/{resident_id}", response_model=ResidentRead)
def get_resident(resident_id: int, db: Session = Depends(get_db)) -> ResidentRead:
    """Fetch a single resident by id. Returns 404 if not found."""
    resident = residents_service.get_resident(db, resident_id)
    if resident is None:
        raise HTTPException(status_code=404, detail="Resident not found")
    return resident
