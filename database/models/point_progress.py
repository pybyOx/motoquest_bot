from peewee import AutoField, ForeignKeyField, DateTimeField, IntegerField, BooleanField

from database.models.base import BaseModel
from database.models.user_session import UserSession
from database.models.point import Point
from playhouse.sqlite_ext import JSONField


class PointProgress(BaseModel):
    """Прохождение пользователем точки в конкретной игре"""
    id = AutoField()
    user_session = ForeignKeyField(UserSession, backref="point_progress", on_delete="CASCADE")
    # UserSession.point_progress - все PointProgress с конкретным UserSession
    point = ForeignKeyField(Point, backref="users_progress", null=True, on_delete="SET NULL")
    # Point.users_progress — все PointProgress с конкретным Point

    started_at = DateTimeField(null=True)
    finished_at = DateTimeField(null=True)

    location_msg_ids = JSONField(default=dict)
    task_msg_ids = JSONField(default=dict)
    solved_msg_ids = JSONField(default=dict)

    clues_used = IntegerField(default=0)
    is_finished = BooleanField(default=False)

    answer_error = BooleanField(default=False)

    @property
    def time(self):
        """Продолжительность прохождения точки (если завершено)"""
        if self.started_at and self.finished_at:
            return self.finished_at - self.started_at
        return None

    class Meta:
        indexes = (
            (('user_session', 'point'), True),
        )

    def __str__(self):
        """PointProgress: <UserSession.__str__>
        \nPoint: <Point.__str__>"""
        return (f"\n PointProgress: {self.user_session}"
                f"\n Point: {self.point}")
