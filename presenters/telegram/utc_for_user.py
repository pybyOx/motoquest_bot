from datetime import datetime, UTC
from zoneinfo import ZoneInfo


def format_utc_for_user(
    dt_utc: datetime,
    user_timezone: str,
    fmt: str = "%d.%m.%Y %H:%M"
) -> str:
    return (
        dt_utc
        .replace(tzinfo=UTC)
        .astimezone(ZoneInfo(user_timezone))
        .strftime(fmt)
    )
