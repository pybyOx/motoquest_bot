from __future__ import annotations
from database.models.user import User
from database.repositories.base_repository import BaseRepository
from core.enums.user_role_types import RoleType
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from core.enums.user_states import UserState


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_or_create_by_id(self, user_id: int, username: str | None = None) -> tuple[User, bool]:

        user, created = self.model.get_or_create(
            id=user_id,
            defaults={"username": username}
        )

        if not created and username and user.username != username:
            user.username = username
            user.save()

        return user, created

    def update_role(self, user_id: int, role: RoleType) -> int:
        return (
            self.model
            .update(role=role)
            .where(self.model.id == user_id)
            .execute()
        )

    def update_state(self, user_id: int, state: UserState) -> int:
        return (
            self.model
            .update(state=state)
            .where(self.model.id == user_id)
            .execute()
        )

    def update_current_session(
            self,
            user_id: int,
            user_session_id: int
    ) -> int:
        # TODO: валидация существования user_session_id —
        #   DeferredForeignKey не создаёт FK-constraint на уровне SQLite
        return (
            self.model
            .update(current_user_session=user_session_id)
            .where(self.model.id == user_id)
            .execute()
        )

    def increment_recovery_attempts(self, user_id: int) -> int:
        return (
            self.model
            .update(recovery_attempts=self.model.recovery_attempts + 1)
            .where(self.model.id == user_id)
            .execute()
        )

    def reset_recovery_attempts(self, user_id: int) -> int:
        return (
            self.model
            .update(recovery_attempts=0)
            .where(self.model.id == user_id)
            .execute()
        )

    def update_if_field_equals(  # TODO: разобраться как работает
            self,
            obj_id: int,
            field: str,
            old_value: Any,
            new_value: Any,
    ) -> bool:
        updated = (
            self.model
            .update(**{field: new_value})
            .where(
                (self.model.id == obj_id) &
                (getattr(self.model, field) == old_value)
            )
            .execute()
        )

        return bool(updated)

    def set_error(self, user_id: int) -> int:
        return (
            self.model
            .update(is_error=True)
            .where(self.model.id == user_id)
            .execute()
        )

    def clear_error(self, user_id: int) -> int:
        return (
            self.model
            .update(is_error=False)
            .where(self.model.id == user_id)
            .execute()
        )

    def reset_ui_msg_id(self, user_id: int) -> int:
        return (
            self.model
            .update(ui_msg_id=None)
            .where(self.model.id == user_id)
            .execute()
        )
