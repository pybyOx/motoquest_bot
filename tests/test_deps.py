import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from api.deps import CurrentUser, get_bot_token
from tests.test_telegram_auth import BOT_TOKEN, USER, make_fields, sign

# Отдельное маленькое приложение: проверяем только зависимость,
# без базы и без настоящих эндпоинтов.
app = FastAPI()


@app.get("/me")
async def me(user: CurrentUser):
    return user


app.dependency_overrides[get_bot_token] = lambda: BOT_TOKEN


async def get_me(headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get("/me", headers=headers)


@pytest.mark.asyncio
async def test_valid_init_data_returns_user():
    response = await get_me({"Authorization": f"tma {sign(make_fields())}"})

    assert response.status_code == 200
    assert response.json() == USER


@pytest.mark.asyncio
@pytest.mark.parametrize("headers", [
    pytest.param({}, id="no-header"),
    pytest.param({"Authorization": "tma "}, id="empty-init-data"),
    pytest.param({"Authorization": "tma"}, id="scheme-only"),
    pytest.param({"Authorization": "Bearer"}, id="other-scheme-only"),
    pytest.param({"Authorization": f"Bearer {sign(make_fields())}"}, id="other-scheme"),
    pytest.param({"Authorization": "tma hash=abc&user=%7B%7D"}, id="bad-signature"),
])
async def test_rejected_with_401(headers):
    response = await get_me(headers)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "tma"
    assert response.json() == {"detail": "Нужен вход через Telegram"}
