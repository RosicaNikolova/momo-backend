"""Simple anomaly detection service.

This module implements a lightweight anomaly detector over the last `limit`
rows for a given resident and metric. The algorithm is intentionally simple and
deterministic:

- Fetch the last `limit` rows (chronological order) using the repository helper.
- Forward-fill/back-fill small gaps.
- Compute the z-score for the window and mark anomalies where |z| >= 3.0.

The endpoint and service intentionally do not expose internal tuning (threshold)
to the API; values are chosen to be conservative for short windows (30 rows).
"""

from typing import Any, List, Tuple
import pandas as pd
from app.repository.insights_repository import get_last_n_metric_rows
from app.schemas.anomaly_get import AnomalyRead


def records_to_df(rows: List[Tuple[Any, Any]]) -> pd.DataFrame:
    """Convert DB rows into a DataFrame.

    The repository returns a list of tuples (date, value) ordered oldest->newest.
    This helper ensures we always have a DataFrame with columns ["date","value"].
    """
    # If no rows, return an empty DataFrame with the expected columns.
    # returning an empty DataFrame lets downstream code call ffill/bfill safely
    return (
        pd.DataFrame(rows, columns=["date", "value"])
        if rows
        else pd.DataFrame(columns=["date", "value"])
    )


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


def compute_anomalies(
    resident_id: int, metric: str, db, limit: int = 30
) -> AnomalyRead | None:
    """Compute anomalies for a resident/metric over the last `limit` rows.

    Returns a plain dict suitable for FastAPI to serialize to `AnomalyRead`.
    If there is no data, returns an empty result (n_anomalies == 0).
    """
    rows = get_last_n_metric_rows(resident_id, metric, limit, db)
    # If repository returned no rows, nothing to analyze -> bail out
    if not rows:
        return None

    # Build a DataFrame for cleaner handling (dates, values)
    # DataFrame columns: ['date', 'value'] with oldest->newest ordering
    df = records_to_df(rows)

    # Fill small gaps using pandas (forward then back fill)
    # - forward fill propagates last known value forward
    # - back fill fills leading NAs with the first available value
    # This keeps interior small gaps from breaking the window analysis.
    df["value"] = df["value"].ffill().bfill()

    # If after filling there are still no numeric values, bail out
    if df["value"].isna().all():
        return None

    # Convert to numeric (floats) - coercing non-numeric entries to NaN
    # (e.g., if DB had stray text); after this we can safely compute mean/std.
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    if df["value"].isna().all():
        return None

    # Population statistics (ddof=0 for population std to match pstdev)
    # mean (mu) and sigma (population standard deviation) are used to compute z-scores.
    mu = df["value"].mean()
    sigma = df["value"].std(ddof=0)

    if sigma == 0 or len(df["value"]) < 2 or pd.isna(sigma):
        return None

    # Conservative threshold for short windows. Kept internal deliberately.
    threshold = 1.0

    # Vectorized z-score computation using pandas Series arithmetic
    # - z = (value - mu) / sigma
    # - mask marks rows where |z| >= threshold
    z_scores = (df["value"] - mu) / sigma
    mask = z_scores.abs() >= threshold

    # Convert results to plain Python types for the response model
    anomalies_idx = [int(i) for i in df.index[mask]]
    # Format anomaly values (seconds) into human-readable strings using the
    # repository-local helper so API returns consistent, user-friendly units.
    anomalies_vals = [format_seconds_h_min(v) for v in df.loc[mask, "value"].tolist()]
    anomalies_dates = df.loc[mask, "date"].tolist()

    n_anom = len(anomalies_idx)
    desc = f"{n_anom} anomalies detected" if n_anom else "no anomalies"

    return AnomalyRead(
        resident_id=resident_id,
        metric=metric,
        n_anomalies=n_anom,
        anomaly_indices=anomalies_idx,
        anomaly_dates=anomalies_dates,
        anomaly_values=anomalies_vals,
        description=desc,
    )
