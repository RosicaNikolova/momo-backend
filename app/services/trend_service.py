from typing import Optional, List, Tuple, Any
from sqlalchemy.orm import Session
import pandas as pd

from app.schemas.trend import TrendRead
from app.repository import insights_repository


BASELINE: int = 28
LAST7: int = 7

# -- helpers ---------------------------------------------------------------


def records_to_df(rows: List[Tuple[Any, Any]]) -> pd.DataFrame:
    """Convert DB rows into a DataFrame.

    The repository returns a list of tuples (date, value) ordered oldest->newest.
    This helper ensures we always have a DataFrame with columns ["date","value"].
    """
    # If no rows, return an empty DataFrame with the expected columns.
    return pd.DataFrame(rows, columns=["date", "value"]) if rows else pd.DataFrame(columns=["date", "value"])


def compute_baseline_last7(values: pd.Series) -> Tuple[float, float]:
    """Compute the baseline (mean of last 28) and last-7 mean from a series.

    - values: pandas Series of numeric metric values (seconds) ordered oldest->newest
    - Returns a tuple (baseline_seconds, last7_seconds). Returns NaN pair if insufficient data.
    """
    if values is None or values.empty or len(values) < LAST7:
        return (float("nan"), float("nan"))
    # baseline uses up to the last 28 records, last7 uses the last 7 records
    baseline_val = values.tail(BASELINE).mean()
    last7_val = values.tail(LAST7).mean()
    return (baseline_val, last7_val)


def format_description(metric_name: str, diff_sec: float) -> str:
    """Return a short human description for the change.

    Examples:
    - "≈ no change"
    - "time in bed decreased by 2h and 35 minutes"
    - "time in bed increased by 30min"

    Notes:
    - diff_sec is in seconds (can be negative). We treat changes under 60s as no change.
    - The description uses absolute hours/minutes for readability and states direction
      via words (increased/decreased).
    """
    if pd.isna(diff_sec):
        return "insufficient data"
    # avoid noisy micro-changes
    if abs(diff_sec) < 60.0:
        return "≈ no change"
    verb = "increased" if diff_sec > 0 else "decreased"
    abs_diff = abs(diff_sec)
    hours = int(abs_diff // 3600)
    minutes = int((abs_diff % 3600) // 60)
    if hours and minutes:
        time_str = f"{hours}h and {minutes} minutes"
    elif hours:
        time_str = f"{hours}h"
    else:
        time_str = f"{minutes} minutes"
    human_metric = metric_name.replace("_", " ")
    return f"{human_metric} {verb} by {time_str}"


def format_seconds_h_min(val_sec: float) -> str:
    """Format seconds into a concise 'Xh Ymin' string.

    - Returns 'N/A' for NaN inputs.
    - Always formats from the absolute value (we don't show a negative unit part).
    - Examples: 9000 -> '2h 30min', 3600 -> '1h', 120 -> '2min'
    """
    if pd.isna(val_sec):
        return "N/A"
    sec = float(val_sec)
    # Use absolute value so unit parts (hours/minutes) are never negative
    sec_abs = abs(sec)
    hours = int(sec_abs // 3600)
    minutes = int((sec_abs % 3600) // 60)
    if hours and minutes:
        return f"{hours}h {minutes}min"
    if hours:
        return f"{hours}h"
    return f"{minutes}min"


# -- main API --------------------------------------------------------------
def compute_trend(resident_id: int, metric: str, db: Session) -> TrendRead | None:
    """Compute a trend insight for a resident's metric.

    Steps:
    1. Fetch up to BASELINE rows from the repository (oldest->newest).
    2. Require at least 7 rows to compute a last-7 average; otherwise return None.
    3. Compute baseline (mean of last 28) and last-7 mean — both in seconds.
    4. Produce a short description (human readable) and format numeric fields as
       hour/minute strings for the API.

    Returns a `TimeInBedInsight` (schema fields are human-readable strings).
    """

    # Fetch rows as (date, value)
    records: List[Tuple[Any, Any]] = insights_repository.get_last_n_metric_rows(
        resident_id, metric, BASELINE, db)

    # quick guard: need at least 7 records to compute a 7-day average
    if not records or len(records) < LAST7:
        return None

    # convert to DataFrame for easy slicing/aggregation
    df = records_to_df(records)
    print(f"data frame: {df}")
    if df.empty or len(df) < 7:
        return None

    # compute baseline and last7 in seconds
    baseline_sec, last7_sec = compute_baseline_last7(df["value"])  # seconds
    difference_sec = last7_sec - baseline_sec
    print(f"difference: {difference_sec}")

    # human-friendly description (uses absolute units but states direction)
    description = format_description(metric, difference_sec)

    # format numeric fields as strings like '2h 30min'
    baseline_hours = format_seconds_h_min(baseline_sec)
    last7_hours = format_seconds_h_min(last7_sec)
    difference_hours = format_seconds_h_min(difference_sec)

    return TrendRead(
        resident_id=resident_id,
        baseline_hours=baseline_hours,
        last_7_days_hours=last7_hours,
        difference_hours=difference_hours,
        description=description,
    )
