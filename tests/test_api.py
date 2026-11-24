from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app
from api.db import get_session
from api.models import GameInfo, GameSession


@pytest.mark.asyncio
async def test_health_returns_ok():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_list_games_returns_games_without_finish(api_session):
    api_session.add_all([
        GameInfo(
            title="Путь дракона",
            slug="way_of_the_dragon",
            description="Тихий путь",
            finish={"text": "Финиш", "link": "https://example.com"},
        ),
        GameInfo(
            title="Вторая игра",
            slug="second_game",
            finish={"text": "Финиш", "link": "https://example.com"},
        ),
    ])
    await api_session.flush()

    async def override_get_session():
        yield api_session

    app.dependency_overrides[get_session] = override_get_session
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/games")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert [game["slug"] for game in data] == ["way_of_the_dragon", "second_game"]
    assert set(data[0]) == {"id", "title", "slug", "description"}
    assert data[0]["description"] == "Тихий путь"
    assert data[1]["description"] == ""


@pytest.mark.asyncio
async def test_schedule_returns_only_upcoming_games_with_title(api_session):
    game = GameInfo(
        title="Путь дракона",
        slug="way_of_the_dragon",
        finish={"text": "Финиш", "link": "https://example.com"},
    )
    api_session.add(game)
    await api_session.flush()

    now = datetime.now(UTC)
    # Связь задаём только через game_info_id, как в живой базе:
    # объект GameInfo к игре не прикреплён, его придётся загрузить.
    api_session.add_all([
        GameSession(game_info_id=game.id, city="Далат", location="Кафе у озера",
                    date=now + timedelta(days=14), timezone="Asia/Ho_Chi_Minh", finished=False),
        GameSession(game_info_id=game.id, city="Нячанг", location="Пирс",
                    date=now + timedelta(days=7), timezone="Asia/Ho_Chi_Minh", finished=False),
        GameSession(game_info_id=game.id, city="Хойан", location="Мост",
                    date=now - timedelta(days=7), timezone="Asia/Ho_Chi_Minh", finished=False),
        GameSession(game_info_id=game.id, city="Сайгон", location="Рынок",
                    date=now + timedelta(days=3), timezone="Asia/Ho_Chi_Minh", finished=True),
    ])
    await api_session.flush()
    # Забываем загруженные объекты: в живом запросе сессия новая и пустая,
    # иначе SQLAlchemy возьмёт GameInfo из памяти и не пойдёт в базу.
    api_session.expunge_all()

    async def override_get_session():
        yield api_session

    app.dependency_overrides[get_session] = override_get_session
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/schedule")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert [item["city"] for item in data] == ["Нячанг", "Далат"]
    assert set(data[0]) == {"id", "city", "date", "timezone", "game_info"}
    assert data[0]["game_info"] == {"title": "Путь дракона"}


@pytest.mark.asyncio
async def test_schedule_game_without_quest_has_null_game_info(api_session):
    # Квест удалили — ondelete="SET NULL" обнулил ссылку, игра в расписании осталась.
    api_session.add(GameSession(
        game_info_id=None, city="Нячанг", location="Пирс",
        date=datetime.now(UTC) + timedelta(days=7), timezone="Asia/Ho_Chi_Minh", finished=False,
    ))
    await api_session.flush()
    api_session.expunge_all()

    async def override_get_session():
        yield api_session

    app.dependency_overrides[get_session] = override_get_session
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/schedule")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["game_info"] is None
