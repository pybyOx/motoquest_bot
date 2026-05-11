from peewee import AutoField, CharField, ForeignKeyField
from playhouse.sqlite_ext import JSONField

from database.models.base import BaseModel
from database.models.game_info import GameInfo


class Point(BaseModel):
    """Информация о точках игры."""
    id = AutoField()
    title = CharField()
    location = JSONField()  # keys: REQ - "link"; OPT - "text", "audio", "image"

    task = JSONField()  # keys: REQ - "text"; OPT - "audio", "image"
    answer = JSONField()  # keys: REQ - "text", "type"
    after_solved = JSONField()  # keys: REQ - "text"; OPT - "audio", "image"

    game_info = ForeignKeyField(GameInfo, backref="points", on_delete="CASCADE")
    # GameInfo.points — все точки игры

    def __str__(self):
        """<title> (<game_info.title>)"""
        return f"{self.title} ({self.game_info.title})"
