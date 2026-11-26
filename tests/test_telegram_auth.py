import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import pytest

from api.telegram_auth import MAX_AGE_SECONDS, verify_init_data
from core.exceptions import InvalidInitData

BOT_TOKEN = "123456:TEST-TOKEN"
USER = {"id": 42, "first_name": "Оксана", "username": "oksana"}


def sign(fields: dict, bot_token: str = BOT_TOKEN) -> str:
    """Подписывает поля так же, как Telegram, и собирает строку initData."""
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    fields_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return urlencode({**fields, "hash": fields_hash})


def make_fields(**overrides) -> dict:
    fields = {
        "query_id": "AAHdF6IQAAAAAN0XohDhrOrc",
        "user": json.dumps(USER, ensure_ascii=False),
        "auth_date": str(int(time.time())),
        "signature": "some-ed25519-signature",
    }
    fields.update(overrides)
    return fields


def test_valid_init_data_returns_user():
    assert verify_init_data(sign(make_fields()), BOT_TOKEN) == USER


def test_tampered_field_fails_signature():
    init_data = sign(make_fields())
    fake_user = json.dumps({**USER, "id": 1}, ensure_ascii=False)
    tampered = init_data.replace(
        urlencode({"user": json.dumps(USER, ensure_ascii=False)}),
        urlencode({"user": fake_user}),
    )
    assert tampered != init_data

    with pytest.raises(InvalidInitData, match="Подпись не совпадает"):
        verify_init_data(tampered, BOT_TOKEN)


def test_other_bot_token_fails_signature():
    init_data = sign(make_fields(), bot_token="999:OTHER-BOT")

    with pytest.raises(InvalidInitData, match="Подпись не совпадает"):
        verify_init_data(init_data, BOT_TOKEN)


def test_missing_hash():
    with pytest.raises(InvalidInitData, match="Нет поля hash"):
        verify_init_data(urlencode(make_fields()), BOT_TOKEN)


def test_expired_auth_date():
    old = int(time.time()) - MAX_AGE_SECONDS - 60

    with pytest.raises(InvalidInitData, match="устарели"):
        verify_init_data(sign(make_fields(auth_date=str(old))), BOT_TOKEN)


def test_auth_date_not_a_number():
    with pytest.raises(InvalidInitData, match="auth_date"):
        verify_init_data(sign(make_fields(auth_date="вчера")), BOT_TOKEN)


def test_user_not_json():
    with pytest.raises(InvalidInitData, match="user"):
        verify_init_data(sign(make_fields(user="не json")), BOT_TOKEN)


def test_missing_user():
    fields = make_fields()
    del fields["user"]

    with pytest.raises(InvalidInitData, match="user"):
        verify_init_data(sign(fields), BOT_TOKEN)
