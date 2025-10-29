# app/schemas.py
from pydantic import BaseModel, ConfigDict
from datetime import date


class TrendRead(BaseModel):
    resident_id: int
    # Human-friendly hour/min strings like "2h 30min" (not raw floats)
    baseline_hours: str
    last_7_days_hours: str
    difference_hours: str
    description: str

    # Pydantic v2: `orm_mode` was renamed to `from_attributes`.
    # Use ConfigDict to set model config compatible with ORM objects.
    model_config = ConfigDict(from_attributes=True)
