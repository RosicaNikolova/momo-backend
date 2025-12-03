from typing import Optional

from pydantic import BaseModel, ConfigDict

# Pydantic model for reading resident


class ResidentRead(BaseModel):
    id: int
    name: str
    room_number: Optional[str] = None

    # Pydantic v2: accept ORM objects via from_attributes
    model_config = ConfigDict(from_attributes=True)
