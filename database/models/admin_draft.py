from peewee import IntegerField, CharField, ForeignKeyField, TextField, DateTimeField
from database.models.base import BaseModel
from database.models.game_info import GameInfo
from database.models.game_session import GameSession


class AdminDraft(BaseModel):
    user_id = IntegerField(primary_key=True)

    game_info = ForeignKeyField(GameInfo, null=True)
    city = CharField(null=True)
    timezone = CharField(null=True)
    location = TextField(null=True)
    date = DateTimeField(null=True)

    game_session = ForeignKeyField(GameSession, null=True, on_delete='SET NULL')
