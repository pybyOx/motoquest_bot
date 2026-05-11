from peewee import ForeignKeyField, CharField

from database.models.base import BaseModel
from database.models.user_session import UserSession


class UserEvent(BaseModel):
    user_session = ForeignKeyField(UserSession, backref="events", on_delete="CASCADE")
    event_type = CharField()

    class Meta:
        indexes = (
            (("user_session", "event_type"), True),
        )
