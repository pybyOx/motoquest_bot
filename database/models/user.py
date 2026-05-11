from peewee import IntegerField, CharField, DeferredForeignKey, BooleanField
from core.enums.user_role_types import RoleType
from core.enums.user_states import UserState

from database.models.base import BaseModel


class User(BaseModel):
    id = IntegerField(primary_key=True)
    username = CharField(null=True)
    role = CharField(default=RoleType.PLAYER)
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
