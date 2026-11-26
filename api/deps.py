import os
from typing import Annotated

from fastapi import Depends, Header, HTTPException

from api.telegram_auth import verify_init_data
from core.exceptions import InvalidInitData


def get_bot_token() -> str:
    return os.environ["BOT_TOKEN"]


async def get_current_user(
    bot_token: Annotated[str, Depends(get_bot_token)],
    authorization: Annotated[str | None, Header()] = None,
) -> dict:
    http_exc = HTTPException(
        status_code=401,
        detail="Нужен вход через Telegram",
        headers={"WWW-Authenticate": "tma"},
    )

    if authorization is None or not authorization.startswith("tma "):
        raise http_exc

    try:
        user = verify_init_data(
            init_data=authorization.removeprefix("tma "),
            bot_token=bot_token,
        )
    except InvalidInitData as err:
        raise http_exc from err

    return user


CurrentUser = Annotated[dict, Depends(get_current_user)]
