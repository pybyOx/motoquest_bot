from peewee import AutoField, CharField
from playhouse.postgres_ext import BinaryJSONField

from database.models.base import BaseModel


class GameInfo(BaseModel):
    """Общая информация об игре."""
    id = AutoField()
    title = CharField(unique=True)
    slug = CharField(unique=True)
    finish = BinaryJSONField()  # keys: REQ - "text", "link"

    def __str__(self):
        """<title>"""
        return f"{self.title}"
