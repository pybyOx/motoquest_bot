from datetime import datetime
from typing import cast
from presenters.telegram.utc_for_user import format_utc_for_user
from peewee import AutoField, ForeignKeyField, CharField, DateTimeField, BooleanField

from database.models.base import BaseModel
from database.models.game_info import GameInfo


class GameSession(BaseModel):
    """Информация о конкретной игре с местом и временем проведения."""
    id = AutoField()

    game_info = ForeignKeyField(GameInfo, backref="games", null=True, on_delete="SET NULL")
    # GameInfo.games - список всех GameSession c информацией GameInfo
    city = CharField(null=True)  # город проведения игры
    location = CharField()  # место встречи
    date = DateTimeField()  # время встречи
    timezone = CharField(null=True)

    finished = BooleanField(default=False)

    class Meta:
        indexes = ((('city', 'date'), True),
                   )

    def __str__(self):
        """
        <game_info.title> 📍 <city> - если есть
        (<DD.MM.YYYY HH:MM>) - в локальном timezone
        """
        date_utc = cast(datetime, self.date)
        timezone = cast(str | None, self.timezone)
        if timezone:
            date_str = format_utc_for_user(date_utc, timezone)
        else:
            date_str = date_utc.strftime("%d.%m.%Y %H:%M")
        city_str = f"📍 {self.city}" if self.city else ""
        return f"{self.game_info.title} {city_str} ({date_str})"
