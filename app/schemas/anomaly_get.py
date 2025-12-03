from datetime import date
from typing import List

from pydantic import BaseModel


class AnomalyRead(BaseModel):
    """Response model for anomaly detection results.

    Fields:
    - resident_id: integer resident identifier
    - metric: metric name used for detection
    - n_anomalies: number of anomalies detected
    - anomaly_indices: list of 0-based indices into the returned window (oldest-first)
    - anomaly_dates: list of dates corresponding to the anomaly indices
    - anomaly_values: list of formatted strings (e.g. '2h 30min') at the anomaly indices
    - description: short human-friendly summary
    """

    resident_id: int
    metric: str
    n_anomalies: int
    anomaly_indices: List[int]
    anomaly_dates: List[date]
    anomaly_values: List[str]
    description: str
