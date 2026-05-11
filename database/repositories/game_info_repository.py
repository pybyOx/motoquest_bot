from database.models.game_info import GameInfo
from database.repositories.base_repository import BaseRepository


class GameInfoRepository(BaseRepository[GameInfo]):
    def __init__(self):
        super().__init__(GameInfo)
