from database.database_model import UserPointProgress, Clue, GameInfo, GameSession, Player, PlayerSession, Point
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
