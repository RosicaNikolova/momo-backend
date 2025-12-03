from enum import Enum

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.anomaly_get import AnomalyRead
from app.schemas.change_point import ChangePointRead
from app.schemas.trend import TrendRead
from app.services import anomaly_service, change_point_service, trend_service


# Router-level allowed metrics
class Metric(str, Enum):
    time_in_bed = "time_in_bed"
    low_activity = "low_activity"
    high_activity = "high_activity"
    at_rest = "at_rest"


# Each router handles one feature (clean separation)
router = APIRouter(prefix="/api/insights", tags=["Insights"])


@router.get("/trend/{metric}/{resident_id}", response_model=TrendRead)
def get_metric_trend(
    metric: Metric, resident_id: int, db: Session = Depends(get_db)
) -> TrendRead:
    """
    Trend endpoint that accepts a metric name and resident id.
    Unknown metrics return HTTP 400.
    """
    # metric is validated by FastAPI against Metric enum; pass string value to service
    insight = trend_service.compute_trend(resident_id, metric.value, db)

    if not insight:
        raise HTTPException(
            status_code=404, detail="No data found for this resident.")
    return insight


@router.get("/changepoints/{metric}/{resident_id}", response_model=ChangePointRead)
def get_metric_changepoints(
    metric: Metric,
    resident_id: int,
    db: Session = Depends(get_db),
) -> ChangePointRead:
    """Detect change points for a metric for a resident using automatic detection.

    - Uses PELT (penalty-based) to select the number of change points.
    - The endpoint inspects the last 30 rows by default.
    """
    # Service handles penalty selection internally; router does not expose tuning.
    result = change_point_service.compute_change_points(
        resident_id, metric.value, db, limit=30
    )
    if not result:
        raise HTTPException(
            status_code=404, detail="No data found or change-point detection failed"
        )
    return result


@router.get("/anomalies/{metric}/{resident_id}", response_model=AnomalyRead)
def get_metric_anomalies(
    metric: Metric,
    resident_id: int,
    db: Session = Depends(get_db),
) -> AnomalyRead:
    """Detect anomalies for the chosen metric and resident.

    - Runs a simple internal z-score based detector on the last 30 rows.
    - The detector uses a conservative threshold and does not expose tuning
      via the API; it's intended as a lightweight anomaly signal for insights.
    """
    result = anomaly_service.compute_anomalies(
        resident_id, metric.value, db, limit=30)
    if not result:
        raise HTTPException(
            status_code=404, detail="No data found or anomaly detection failed"
        )
    return result
