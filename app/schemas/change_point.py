from pydantic import BaseModel, ConfigDict
from typing import List


class ChangePointRead(BaseModel):
    resident_id: int
    metric: str
    n_change_points: int
    # indices in the returned series (0-based)
    change_point_indices: List[int]
    # ISO dates for the change points (string form)
    change_point_dates: List[str]
    # formatted values at the change points (e.g. '2h 30min')
    change_point_values: List[str]
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)
