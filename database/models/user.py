from peewee import IntegerField, CharField, DeferredForeignKey, BooleanField
from core.enums.user_role_types import RoleType
from core.enums.user_states import UserState

from database.models.base import BaseModel


class User(BaseModel):
    id = IntegerField(primary_key=True)
    username = CharField(null=True)
    role = CharField(default=RoleType.PLAYER)
    # TODO: рефакторинг для настоящего FK constraint.
    #   DeferredForeignKey разрешает циклический импорт User <-> UserSession на уровне Python,
    #   но peewee НЕ создаёт SQL FOREIGN KEY constraint в DDL для такого поля.
    #   То есть SQLite принимает любой int в current_user_session_id, даже несуществующий,
    #   даже при pragma foreign_keys=1. Целостность гарантируется только в сервисном слое.
    #   Решение: разорвать циклическую зависимость моделей (например, хранить связь однонаправленно).
    current_user_session = DeferredForeignKey("UserSession", null=True, backref='current_users',
                                              deferrable='INITIALLY DEFERRED', on_delete="SET NULL")
    # UserSession.current_users — все User с конкретным UserSession
    state = CharField(default=UserState.idle)
    recovery_attempts = IntegerField(default=0)
    is_error = BooleanField(default=False)

    ui_msg_id = IntegerField(null=True)

    @property
    def is_admin(self) -> bool:
        return self.role == RoleType.ADMIN

    def __str__(self):
        """<username or 'user'> (<id>)"""
        return f"@{self.username or 'user'} ({self.id})"
