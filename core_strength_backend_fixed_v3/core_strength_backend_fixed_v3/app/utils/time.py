from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone as fixed_timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.core.config import settings


def _load_local_timezone():
    """Tải múi giờ cấu hình.

    Windows thường không có sẵn IANA time-zone database. Package ``tzdata``
    trong requirements.txt là nguồn chính. Fallback UTC+07:00 giúp backend vẫn
    khởi động đối với Asia/Ho_Chi_Minh nếu môi trường chưa cài tzdata.
    """
    try:
        return ZoneInfo(settings.timezone)
    except ZoneInfoNotFoundError as exc:
        if settings.timezone == "Asia/Ho_Chi_Minh":
            return fixed_timezone(timedelta(hours=7), name="Asia/Ho_Chi_Minh")
        raise RuntimeError(
            f"Không tìm thấy múi giờ {settings.timezone!r}. "
            "Hãy chạy: python -m pip install tzdata"
        ) from exc


LOCAL_TZ = _load_local_timezone()


def now_local() -> datetime:
    """Trả về thời gian local dạng naive để khớp MySQL DATETIME."""
    return datetime.now(LOCAL_TZ).replace(tzinfo=None)


def today_local() -> date:
    return datetime.now(LOCAL_TZ).date()


def as_local_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=LOCAL_TZ)
    else:
        value = value.astimezone(LOCAL_TZ)
    return value.isoformat()


def start_of_day(value: date) -> datetime:
    return datetime.combine(value, time.min)


def end_of_day(value: date) -> datetime:
    return datetime.combine(value, time.max)


def month_bounds(value: date | None = None) -> tuple[datetime, datetime]:
    target = value or today_local()
    start = datetime(target.year, target.month, 1)
    if target.month == 12:
        next_month = datetime(target.year + 1, 1, 1)
    else:
        next_month = datetime(target.year, target.month + 1, 1)
    return start, next_month - timedelta(microseconds=1)
