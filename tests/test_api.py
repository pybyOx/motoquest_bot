import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app
from api.db import get_session
from api.models import GameInfo


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
