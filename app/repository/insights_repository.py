from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.orm_models.inbed_daily import InBedDaily
from typing import List, Tuple, Any


# def get_last_n_rows(db: Session, resident_id: int, n: int) -> List[Tuple[Any, Any]]:
#     """
#     Return up to last `n` rows as a list of plain tuples (date, time_in_bed),
#     ordered chronologically (oldest first).

#     Implementation:
#     - Query the most recent `n` rows (DESC by date) selecting only the
#         date and time_in_bed columns.
#     - Reverse the small result list to chronological order.
#     - Convert each SQLAlchemy Row into a plain tuple before returning so
#         the runtime type matches the annotated return type.
#     """
#     rows = (
#         db.query(InBedDaily.date, InBedDaily.time_in_bed)
#         .filter(InBedDaily.resident_id == resident_id)
#         .order_by(desc(InBedDaily.date))
#         .limit(n)
#         .all()
#     )

#     # rows is newest-first; reverse to oldest-first (chronological)
#     rows = list(reversed(rows))
#     print(rows)
#     # Convert to plain tuples (date, time_in_bed) to satisfy static typing
#     return [(r[0], r[1]) for r in rows]


def get_last_n_metric_rows(
    resident_id: int, metric: str, limit: int, db: Session
) -> List[Tuple[Any, Any]]:
    """Return up to last `n` rows as (date, value) for a chosen metric.

    Allowed metrics map to columns on the InBedDaily model. Returns rows in
    chronological order (oldest first).
    """
    # map metric name to column attribute
    metric_map = {
        "time_in_bed": InBedDaily.time_in_bed,
        "low_activity": InBedDaily.low_activity,
        "high_activity": InBedDaily.high_activity,
        "at_rest": InBedDaily.at_rest,
    }

    col = metric_map.get(metric)
    if col is None:
        raise ValueError(f"Unknown metric: {metric}")

    rows = (
        db.query(InBedDaily.date, col)
        .filter(InBedDaily.resident_id == resident_id)
        .order_by(desc(InBedDaily.date))
        .limit(limit)
        .all()
    )
    rows = list(reversed(rows))
    return [(r[0], r[1]) for r in rows]
