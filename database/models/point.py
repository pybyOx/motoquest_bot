from peewee import AutoField, CharField, ForeignKeyField
from playhouse.postgres_ext import BinaryJSONField

from database.models.base import BaseModel
from database.models.game_info import GameInfo


class Point(BaseModel):
    """Информация о точках игры."""
    id = AutoField()
    title = CharField()
    location = BinaryJSONField()  # keys: REQ - "link"; OPT - "text", "audio", "image"

    task = BinaryJSONField()  # keys: REQ - "text"; OPT - "audio", "image"
    answer = BinaryJSONField()  # keys: REQ - "text", "type"
    after_solved = BinaryJSONField()  # keys: REQ - "text"; OPT - "audio", "image"

    game_info = ForeignKeyField(GameInfo, backref="points", on_delete="CASCADE")
    # GameInfo.points — все точки игры

    def __str__(self):
        """<title> (<game_info.title>)"""
        return f"{self.title} ({self.game_info.title})"
