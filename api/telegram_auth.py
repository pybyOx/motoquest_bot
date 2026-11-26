import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

from core.exceptions import InvalidInitData

MAX_AGE_SECONDS = 24 * 60 * 60


def verify_init_data(init_data: str, bot_token: str) -> dict:
    data = dict(parse_qsl(init_data))

    received_hash = data.pop("hash", None)
    if received_hash is None:
        raise InvalidInitData("Нет поля hash")

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))

    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(received_hash, expected_hash):
        raise InvalidInitData("Подпись не совпадает")

    try:
        auth_date = int(data["auth_date"])
    except (KeyError, ValueError) as err:
        raise InvalidInitData("Нет поля auth_date или оно не число") from err

    if (time.time() - auth_date) > MAX_AGE_SECONDS:
        raise InvalidInitData("initData устарели")

    try:
        user = json.loads(data["user"])
    except (KeyError, json.JSONDecodeError) as err:
        raise InvalidInitData("Нет поля user или оно не JSON") from err

    return user
