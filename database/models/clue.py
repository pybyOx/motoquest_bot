from peewee import ForeignKeyField, TextField, IntegerField

from database.models.base import BaseModel
from database.models.point import Point


class Clue(BaseModel):
    """Подсказки к каждой точке (их 3 максимум)"""
    point = ForeignKeyField(Point, backref="clues", on_delete="CASCADE")
    text = TextField()
    order = IntegerField()  # 1, 2, 3

    class Meta:
        indexes = (
            (("point", "order"), True),  # уникальность order внутри point
        )
