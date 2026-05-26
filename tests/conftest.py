import pytest
from playhouse.sqlite_ext import SqliteExtDatabase

from database.models.user import User
from database.models.user_session import UserSession
from database.models.game_session import GameSession
from database.models.game_info import GameInfo
from database.models.point import Point
from database.models.point_progress import PointProgress
from database.models.clue import Clue
from database.models.user_event import UserEvent
from database.models.admin_draft import AdminDraft

from database.repositories.user_repository import UserRepository
from database.repositories.user_event_repository import UserEventRepository
from database.repositories.game_session_repository import GameSessionRepository
from database.repositories.user_session_repository import UserSessionRepository
from database.repositories.point_progress_repository import PointProgressRepository


from datetime import datetime, UTC

ALL_MODELS = [
    User,
    UserSession,
    GameSession,
    GameInfo,
    Point,
    PointProgress,
    Clue,
    UserEvent,
    AdminDraft,
]


@pytest.fixture
def test_db():
    db = SqliteExtDatabase(":memory:", pragmas={"foreign_keys": 1})
    db.bind(ALL_MODELS, bind_refs=False, bind_backrefs=False)
    db.connect()
    db.create_tables(ALL_MODELS)

    yield db

    db.drop_tables(ALL_MODELS)
    db.close()


@pytest.fixture
def user(user_repo):
    user, _ = user_repo.get_or_create_by_id(user_id=123, username="oksana")
    return user


@pytest.fixture
def other_user(user_repo):
    user, _ = user_repo.get_or_create_by_id(user_id=456, username="maria")
    return user


@pytest.fixture
def user_repo(test_db):
    return UserRepository()


@pytest.fixture
def user_event_repo(test_db):
    return UserEventRepository()


@pytest.fixture
def game_info(test_db):
    return GameInfo.create(
        title="Test Quest",
        slug="test-quest",
        finish={"text": "Финиш", "link": "https://example.com"},
    )


@pytest.fixture
def game_session(test_db):
    return GameSession.create(
        location="A",
        date=datetime(2026, 6, 1, 12, 0),
    )


@pytest.fixture
def other_game_session(test_db):
    return GameSession.create(
        location="B",
        date=datetime(2026, 6, 1, 12, 0),
    )


@pytest.fixture
def finished_game_session(test_db):
    return GameSession.create(
        location="C",
        date=datetime(2026, 6, 1, 12, 0),
        finished=True
    )


@pytest.fixture
def game_session_repo(test_db):
    return GameSessionRepository()


@pytest.fixture
def user_session(user, game_session):
    return UserSession.create(user=user, game_session=game_session)


@pytest.fixture
def other_user_session(other_user, game_session):
    return UserSession.create(user=other_user, game_session=game_session)


@pytest.fixture
def user_session_repo(test_db):
    return UserSessionRepository()


@pytest.fixture
def point_progress(user_session):
    return PointProgress.create(user_session=user_session)


@pytest.fixture
def other_point_progress(user_session):
    return PointProgress.create(user_session=user_session)


@pytest.fixture
def point_progress_repo(test_db):
    return PointProgressRepository()


@pytest.fixture
def point(game_info):
    return Point.create(
        title="Точка 1",
        location={"link": "https://maps.example.com"},
        task={"text": "Задание"},
        answer={"text": "ответ", "type": "text"},
        after_solved={"text": "Решено"},
        game_info=game_info,
    )


@pytest.fixture
def existing_datetime():
    return datetime(2026, 6, 1, 12, 0, tzinfo=UTC)
