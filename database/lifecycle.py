from config_data.config import get_config
from database.db import db, database_params
from database.models.user_event import UserEvent
from database.models.point_progress import PointProgress
from database.models.user_session import UserSession
from database.models.user import User
from database.models.game_session import GameSession
from database.models.clue import Clue
from database.models.point import Point
from database.models.game_info import GameInfo
from database.models.admin_draft import AdminDraft


def create_models():
    db.create_tables(
        [
            AdminDraft,
            Clue,
            GameInfo,
            GameSession,
            Point,
            PointProgress,
            User,
            UserEvent,
            UserSession,
        ],
        safe=True
    )


def setup_db():
    """Инициализирует базу параметрами из конфига и открывает соединение.

    Чтение DATABASE_URL происходит здесь, а не на импорте: если переменной нет,
    приложение падает при старте с понятной ошибкой, а импорт моделей
    (например, в тестах) остаётся безвредным.
    """
    if db.database is None:
        db.init(**database_params(get_config().database_url))
    if db.is_closed():
        db.connect()


def close_db():
    if not db.is_closed():
        db.close()
