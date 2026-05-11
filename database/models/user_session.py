from peewee import AutoField, ForeignKeyField, CharField
from playhouse.sqlite_ext import JSONField

from core.enums.session_states import SessionState
from database.models.base import BaseModel
from database.models.game_session import GameSession
from database.models.user import User
from database.models.point import Point


class UserSession(BaseModel):
    """Промежуточная таблица между конкретным игроком и игровой сессией."""
    id = AutoField()
    user = ForeignKeyField(User, backref="user_sessions", deferrable='INITIALLY DEFERRED')
    # User.user_sessions — все UserSession с конкретным User
    game_session = ForeignKeyField(GameSession, backref="user_sessions", on_delete="CASCADE")
    # GameSession.user_sessions — все UserSession с конкретной GameSession
    current_point = ForeignKeyField(Point, null=True, backref="current_users", on_delete="SET NULL")
    # Point.current_users - все UserSession с конкретным Point
    state = CharField(
        choices=[(s, s) for s in SessionState],
        default=SessionState.REGISTERED
    )
    finish_msg_ids = JSONField(default=dict)

    class Meta:
        indexes = (
            (('user', 'game_session'), True),  # уникальность пары (user, game_session)
        )

    def __str__(self):
        """GameSession: <GameSession.__str__> (id: <id>)
        \nUser: <User.__str__>"""
        return (f"\n GameSession: {self.game_session} (id: {self.game_session.id})"
                f"\n User: {self.user}")
