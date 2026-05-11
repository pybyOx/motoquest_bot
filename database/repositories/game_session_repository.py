from database.models.game_session import GameSession
from database.repositories.base_repository import BaseRepository
from peewee import ModelSelect


class GameSessionRepository(BaseRepository[GameSession]):
    def __init__(self):
        super().__init__(GameSession)

    def get_active(self) -> ModelSelect:
        return (
            self.model
            .select()
            .where(self.model.finished == False)
        )

    def set_finished(self, game_session_id: int) -> int:
        return (
            self.model
            .update(finished=True)
            .where(self.model.id == game_session_id)
            .execute()
        )
