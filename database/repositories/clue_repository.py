from __future__ import annotations
from database.models.clue import Clue
from database.repositories.base_repository import BaseRepository
from peewee import Model
from typing import TYPE_CHECKING, TypeVar
if TYPE_CHECKING:
    from peewee import ModelSelect

T = TypeVar("T", bound=Model)


class ClueRepository(BaseRepository[Clue]):
    def __init__(self):
        super().__init__(Clue)

    def get_clues_up_to(self, point_id: int, max_order: int) -> ModelSelect:
        return (
            self.model
            .select()
            .where(
                (self.model.point_id == point_id) &
                (self.model.order <= max_order)
            )
            .order_by(self.model.order)
        )
