from __future__ import annotations
from database.models.admin_draft import AdminDraft
from database.repositories.base_repository import BaseRepository
from typing import TypeVar
from peewee import Model

T = TypeVar("T", bound=Model)


class AdminDraftRepository(BaseRepository[AdminDraft]):
    def __init__(self):
        super().__init__(AdminDraft)

    def reset_all(self, user_id: int) -> int:
        return (
            self.model
            .update(
                game_info=None,
                city=None,
                timezone=None,
                location=None,
                date=None,
                game_session=None,
            )
            .where(self.model._meta.primary_key == user_id)
            .execute()
        )
