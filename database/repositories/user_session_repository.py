from __future__ import annotations
from typing import TYPE_CHECKING
from core.enums.session_states import SessionState
from database.models.user_session import UserSession
from database.repositories.base_repository import BaseRepository


if TYPE_CHECKING:
    from peewee import ModelSelect


class UserSessionRepository(BaseRepository[UserSession]):
    def __init__(self):
        super().__init__(UserSession)

    def start_session(self, user_session_id: int) -> int:
        return (
            self.model
            .update(state=SessionState.STARTED)
            .where(self.model.id == user_session_id)
            .execute()
        )

    def finish_session(self, user_session_id: int) -> int:
        return (
            self.model
            .update(state=SessionState.FINISHED)
            .where(self.model.id == user_session_id)
            .execute()
        )

    def get_registered(self, user_id: int) -> ModelSelect:
        return (
            self.model
            .select()
            .where(
                (self.model.user == user_id) &
                (self.model.state == SessionState.REGISTERED)
            )
        )

    def set_current_point(self, user_session_id: int, point_id: int) -> int:
        return (
            self.model
            .update(current_point=point_id)
            .where(self.model.id == user_session_id)
            .execute()
        )

    def has_non_finished(self, game_session_id: int) -> bool:
        return (
            self.model
            .select()
            .where(
                (self.model.game_session == game_session_id) &
                (self.model.state != SessionState.FINISHED)
            )
            .exists()
        )
