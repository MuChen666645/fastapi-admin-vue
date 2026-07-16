"""Application time helpers."""

from datetime import datetime, timedelta, timezone


UTC8 = timezone(timedelta(hours=8), name="UTC+08:00")


def now_utc8() -> datetime:
    """Return the current timezone-aware UTC+8 time."""
    return datetime.now(UTC8)


def now_utc8_naive() -> datetime:
    """Return UTC+8 local time for storage in MySQL DATETIME columns."""
    return now_utc8().replace(tzinfo=None)
