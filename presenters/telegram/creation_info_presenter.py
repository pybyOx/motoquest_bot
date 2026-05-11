from presenters.telegram.html import bold
from presenters.telegram.utc_for_user import format_utc_for_user
from presenters.telegram.render_location import render_location
from datetime import datetime


def build_session_info_text(
        game_title: str,
        city_title: str,
        location: str,
        date_utc: datetime,
        timezone: str,
) -> str:
    return (f"Игра: {bold(game_title)}\n"
            f"Город: {city_title}\n"
            f"{render_location(location)}\n"
            f"Дата: {format_utc_for_user(date_utc, timezone)}")
