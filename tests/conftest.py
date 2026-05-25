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

from datetime import datetime

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
def user_repo(test_db):
    return UserRepository()


@pytest.fixture
def existing_user(user_repo):
    user, _ = user_repo.get_or_create_by_id(user_id=123, username="oksana")
    return user


@pytest.fixture
def game_session(test_db):
    return GameSession.create(
        location="Парк Горького",
        date=datetime(2026, 6, 1, 12, 0),
    )


@pytest.fixture
def user_session(existing_user, game_session):
    return UserSession.create(user=existing_user, game_session=game_session)
