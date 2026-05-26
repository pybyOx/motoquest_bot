from __future__ import annotations
from datetime import datetime, UTC
from database.models.point_progress import PointProgress
from database.repositories.base_repository import BaseRepository
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.user_session import UserSession
    from peewee import ModelSelect


class PointProgressRepository(BaseRepository[PointProgress]):
    def __init__(self):
        super().__init__(PointProgress)

    def create_for_session(
            self,
            user_session_id: int,
            point_ids: list[int],
    ) -> None:
        self.model.insert_many(
            [
                {
                    "user_session": user_session_id,
                    "point": point_id
                }
                for point_id in point_ids
            ]
        ).execute()

    def start_progress(
            self,
            point_progress_id: int,
            started_at: datetime | None = None,
    ) -> int:
        return (
            self.model
            .update(started_at=started_at or datetime.now(UTC))
            .where(self.model.id == point_progress_id)
            .execute()
        )

    def finish_progress(
            self,
            point_progress_id: int,
            finished_at: datetime | None = None,
    ) -> int:
        return (
            self.model
            .update(
                finished_at=finished_at or datetime.now(UTC),
                is_finished=True
            )
            .where(self.model.id == point_progress_id)
            .execute()
        )

    def get_non_finished_by_session(self, user_session_id: int) -> ModelSelect:
        return (
            self.model
            .select()
            .where(
                (self.model.user_session == user_session_id) &
                (self.model.is_finished == False)
            )
        )

    def has_non_finished(self, user_session_id: int) -> bool:
        return (
            self.model
            .select()
            .where(
                (self.model.user_session == user_session_id) &
                (self.model.is_finished == False)
            )
            .exists()
        )

    def get_current_by_session(self, user_session: UserSession) -> PointProgress | None:

        return self.model.get_or_none(
            (self.model.user_session == user_session) &
            (self.model.point == user_session.current_point)
        )

    def increment_clues_used(
            self,
            point_progress_id: int,
            max_clues: int = 3
    ) -> int | None:
        """
        Увеличивает счётчик использованных подсказок на 1,
        если лимит не превышен.

        :return: Новое значение clues_used или None, если лимит достигнут
        """
        updated = (
            self.model
            .update(clues_used=self.model.clues_used + 1)
            .where(
                (self.model.id == point_progress_id) &
                (self.model.clues_used < max_clues)
            )
            .execute()
        )
        if updated != 1:
            return None

        return (
            self.model
            .select(self.model.clues_used)
            .where(self.model.id == point_progress_id)
            .scalar()
        )
