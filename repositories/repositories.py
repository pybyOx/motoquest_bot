from database.database_model import (UserPointProgress, Clue, GameInfo, GameSession,
                                     Player, PlayerSession, Point, PlayerEvent)
from repositories.base_repository import BaseRepository


class UserPointProgressRepository(BaseRepository):
    model = UserPointProgress


class ClueRepository(BaseRepository):
    model = Clue


class GameInfoRepository(BaseRepository):
    model = GameInfo


class GameSessionRepository(BaseRepository):
    model = GameSession


class PlayerRepository(BaseRepository):
    model = Player


class PlayerSessionRepository(BaseRepository):
    model = PlayerSession


class PointRepository(BaseRepository):
    model = Point


class PlayerEventRepository(BaseRepository):
    model = PlayerEvent

    @classmethod
    def exists(cls, player_session, event_type: str) -> bool:
        return cls.model.select().where(
            (cls.model.player_session == player_session) &
            (cls.model.event_type == event_type)
        ).exists()

