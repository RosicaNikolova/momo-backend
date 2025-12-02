from typing import List, Tuple, Any
from sqlalchemy.orm import Session
import pandas as pd
import ruptures as rpt
import numpy as np
from app.repository import insights_repository
from app.schemas.change_point import ChangePointRead


def _format_seconds_h_min(val_sec: float) -> str:
    """Format seconds into a concise 'Xh Ymin' string.

    Uses absolute value to produce stable unit strings.
    """
    if pd.isna(val_sec):
        return "N/A"
    sec_abs = abs(float(val_sec))
    hours = int(sec_abs // 3600)
    minutes = int((sec_abs % 3600) // 60)
    if hours and minutes:
        return f"{hours}h {minutes}min"
    if hours:
        return f"{hours}h"
    return f"{minutes}min"


def records_to_df(rows: List[Tuple[Any, Any]]) -> pd.DataFrame:
    """Convert DB rows into a DataFrame.
    The repository returns a list of tuples (date, value) ordered oldest->newest.
    """
    # If no rows, return an empty DataFrame with the expected columns.
    return (
        pd.DataFrame(rows, columns=["date", "value"])
        if rows
        else pd.DataFrame(columns=["date", "value"])
    )


def compute_change_points(
    resident_id: int, metric: str, db: Session, limit: int = 30
) -> ChangePointRead | None:
    """Detect change points on the last `limit` rows for `metric`.

    Uses the PELT algorithm with an l2 cost and a penalty parameter to select
    the number of change points automatically. If `pen` is None the function
    computes a simple heuristic based on the signal variance and length.

    Returns None when insufficient data.
    """
    # fetch rows (date, value) returned oldest->newest
    rows: List[Tuple[Any, Any]] = insights_repository.get_last_n_metric_rows(
        resident_id, metric, limit, db
    )
    if not rows or len(rows) < 2:
        return None

    df = records_to_df(rows)  # oldest->newest
    # prepare numeric signal; fill small gaps
    print(f"data frame: {df}")
    # use explicit ffill()/bfill() to satisfy pandas stubs and linters
    signal = df["value"].ffill().bfill().to_numpy()
    print(f"signal: {signal}")
    # ensure 2D signal is acceptable to ruptures (univariate -> 1d is fine)

    if signal.size == 0:
        return None

    # Auto-only behavior: standardize the signal (z-score) and use PELT with a
    # heuristic penalty when none is provided. Standardizing makes the penalty
    # easier to reason about across different residents/metrics.
    n = len(signal)
    sig = signal.astype(float)
    mean = float(np.mean(sig)) if n > 0 else 0.0
    std = float(np.std(sig, ddof=0)) if n > 0 else 0.0
    print(f"mean: {mean}, std: {std}")
    if std > 0:
        sig_std = (sig - mean) / std
    else:
        # constant signal -> zero-centered; no variance to exploit
        sig_std = sig - mean

    # pen = 3.0 * float(np.log(n + 1))

    pen = 1
    algo = rpt.Pelt(model="l2").fit(sig_std)
    print(f"using penalty: {pen}")
    print(f"signal (std): {sig_std}")

    # sensitivity
    bkps = algo.predict(pen=pen)

    print(f"breakpoints: {bkps}")
    # Convert breakpoints to 0-based indices for the last element of each segment (exclude final len)
    cp_indices = [b - 1 for b in bkps if b - 1 < len(signal) and b - 1 >= 0]
    # Remove possible duplicate of final index
    cp_indices = [i for i in cp_indices if i < len(signal) - 1]

    # map to dates and formatted values
    cp_dates = [str(df.iloc[i]["date"]) for i in cp_indices]
    cp_values = [_format_seconds_h_min(df.iloc[i]["value"]) for i in cp_indices]

    description = f"Detected {len(cp_indices)} change points using PELT (l2) over last {len(df)} days."

    return ChangePointRead(
        resident_id=resident_id,
        metric=metric,
        n_change_points=len(cp_indices),
        change_point_indices=cp_indices,
        change_point_dates=cp_dates,
        change_point_values=cp_values,
        description=description,
    )
