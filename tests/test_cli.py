"""Тесты cli-команд: create_game, set_admin, recover_user.

Команды ходят в базу через контейнер зависимостей. В тестах контейнер
подменяется на набор репозиториев, привязанных к тестовой базе, — так
проверяется настоящая логика команды, а не её имитация.
"""

import json
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from cli import create_game as create_game_module
from cli import recover_user as recover_user_module
from cli import set_admin as set_admin_module
from core.enums.user_role_types import RoleType
from core.exceptions import AlreadyExistsError
from core.utils import check_data
from database.models.clue import Clue
from database.models.game_info import GameInfo
from database.models.point import Point
from database.repositories.clue_repository import ClueRepository
from database.repositories.game_info_repository import GameInfoRepository
from database.repositories.point_repository import PointRepository
from database.repositories.user_repository import UserRepository

MAP_LINK = "https://www.openstreetmap.org/node/1"

VALID_GAME = {
    "title": "Тестовый квест",
    "slug": "test-quest",
    "description": "Короткий квест по набережной",
    "finish": {"text": "Финиш", "link": MAP_LINK},
    "points": [
        {
            "title": "Первая точка",
            "location": {"link": MAP_LINK},
            "task": {"text": "Найди табличку"},
            "answer": {"type": "text", "text": "дракон"},
            "clues": ["подсказка раз", "подсказка два", "подсказка три"],
            "after_solved": {"text": "Верно!"},
        }
    ],
}


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """Проверка доступности ссылок на карты не должна ходить в сеть."""
    monkeypatch.setattr(check_data, "is_url_accessible", lambda url: True)


@pytest.fixture
def game_file(tmp_path):
    path = tmp_path / "game.json"
    path.write_text(json.dumps(VALID_GAME, ensure_ascii=False), encoding="utf-8")
    return path


@pytest.fixture
def create_game(monkeypatch, test_db):
    container = SimpleNamespace(
        game_info_repo=GameInfoRepository(),
        point_repo=PointRepository(),
        clue_repo=ClueRepository(),
    )
    monkeypatch.setattr(create_game_module, "get_container", lambda: container)
    return create_game_module.create_game


# ── create_game ───────────────────────────────────────────────────────────

def test_create_game_creates_game_points_and_clues(create_game, game_file):
    create_game(str(game_file))

    game = GameInfo.get(GameInfo.slug == "test-quest")
    assert game.title == "Тестовый квест"
    assert game.description == "Короткий квест по набережной"
    assert game.finish == {"text": "Финиш", "link": MAP_LINK}

    point = Point.get(Point.game_info == game)
    assert point.title == "Первая точка"
    assert point.answer == {"type": "text", "text": "дракон"}

    clues = Clue.select().where(Clue.point == point).order_by(Clue.order)
    assert [clue.text for clue in clues] == [
        "подсказка раз", "подсказка два", "подсказка три",
    ]
    assert [clue.order for clue in clues] == [1, 2, 3]


def test_create_game_exits_when_file_missing(create_game, tmp_path):
    with pytest.raises(SystemExit) as exit_info:
        create_game(str(tmp_path / "нет-такого.json"))

    assert exit_info.value.code == 1
    assert GameInfo.select().count() == 0


@pytest.mark.parametrize("broken_part", [
    {"finish": None},       # обязательное поле удалено
    {"description": None},  # описание для витрины обязательно
    {"description": ""},    # и не может быть пустым
])
def test_create_game_exits_when_schema_violated(create_game, tmp_path, broken_part):
    broken = {**VALID_GAME, **broken_part}
    broken = {key: value for key, value in broken.items() if value is not None}
    path = tmp_path / "broken.json"
    path.write_text(json.dumps(broken, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(SystemExit) as exit_info:
        create_game(str(path))

    assert exit_info.value.code == 1
    assert GameInfo.select().count() == 0


def test_create_game_leaves_nothing_when_fails_halfway(create_game, tmp_path, monkeypatch):
    """Ошибка на середине загрузки не должна оставлять в базе недосозданную игру."""
    second_point = {**VALID_GAME["points"][0], "title": "Вторая точка"}
    game = {**VALID_GAME, "points": [VALID_GAME["points"][0], second_point]}
    path = tmp_path / "game.json"
    path.write_text(json.dumps(game, ensure_ascii=False), encoding="utf-8")

    original_create = ClueRepository.create
    created_clues = []

    def fail_on_second_point(self, data):
        if data["point"].title == "Вторая точка":
            raise AlreadyExistsError("подсказка уже существует")
        created_clues.append(data)
        return original_create(self, data)

    monkeypatch.setattr(ClueRepository, "create", fail_on_second_point)

    with pytest.raises(SystemExit) as exit_info:
        create_game(str(path))

    assert len(created_clues) == 3  # первая точка успела загрузиться целиком
    assert exit_info.value.code == 1
    assert GameInfo.select().count() == 0
    assert Point.select().count() == 0
    assert Clue.select().count() == 0


# ── set_admin ───────────────────────────────────────────────────────────

def test_set_admin_gives_admin_role(monkeypatch, test_db):
    container = SimpleNamespace(user_repo=UserRepository())
    monkeypatch.setattr(set_admin_module, "get_container", lambda: container)

    set_admin_module.set_admin(395578226)

    user = container.user_repo.get_by_id(395578226)
    assert user.role == RoleType.ADMIN


# ── recover_user ───────────────────────────────────────────────────────────

def test_recover_user_calls_service(monkeypatch):
    service = MagicMock()
    monkeypatch.setattr(
        recover_user_module, "get_container",
        lambda: SimpleNamespace(user_states_service=service),
    )

    recover_user_module.recover_user(123)

    service.recover.assert_called_once_with(user_id=123)


# ── точки входа: база должна подниматься до работы с ней ──────────────────

@pytest.mark.parametrize(
    "module, worker, argv, expected_argument",
    [
        (create_game_module, "create_game", ["cli", "game.json"], "game.json"),
        (set_admin_module, "set_admin", ["cli", "395578226"], 395578226),
        (recover_user_module, "recover_user", ["cli", "123"], 123),
    ],
    ids=["create_game", "set_admin", "recover_user"],
)
def test_main_initialises_database_before_work(
    monkeypatch, module, worker, argv, expected_argument
):
    """Регрессия: команды запускаются отдельным процессом и обязаны сами звать setup_db.

    Объект базы создаётся без параметров, и без setup_db первый же запрос
    падает с InterfaceError.
    """
    calls = []
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(module, "setup_db", lambda: calls.append("setup_db"))
    monkeypatch.setattr(module, worker, lambda value: calls.append(("работа", value)))

    module.main()

    assert calls == ["setup_db", ("работа", expected_argument)]
