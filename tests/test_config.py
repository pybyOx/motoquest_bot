import dataclasses

import pytest

from config_data import config
from config_data.config import Config, get_config, load_config
from core.exceptions import ConfigError


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Изолирует тесты от реального окружения и от файла .env.

    load_dotenv() подменён заглушкой: иначе load_config() подтянул бы
    значения из настоящего .env разработчика, и тест на отсутствующую
    переменную проходил бы в CI, но падал локально.
    """
    monkeypatch.setattr(config, "load_dotenv", lambda *args, **kwargs: False)
    for name in ("BOT_TOKEN", "MAIN_ADMIN_ID", "INSPECTOR_ID"):
        monkeypatch.delenv(name, raising=False)
    get_config.cache_clear()
    yield
    get_config.cache_clear()


def set_env(monkeypatch, **values):
    for name, value in values.items():
        monkeypatch.setenv(name, value)


# ── load_config ───────────────────────────────────────────────────────────

def test_load_config_reads_all_values(monkeypatch):
    set_env(
        monkeypatch,
        BOT_TOKEN="123:abc",
        MAIN_ADMIN_ID="42",
        INSPECTOR_ID="7",
    )

    cfg = load_config()

    assert cfg == Config(bot_token="123:abc", main_admin_id=42, inspector_id=7)


def test_load_config_converts_ids_to_int(monkeypatch):
    set_env(monkeypatch, BOT_TOKEN="t", MAIN_ADMIN_ID="42", INSPECTOR_ID="7")

    cfg = load_config()

    assert isinstance(cfg.main_admin_id, int)
    assert isinstance(cfg.inspector_id, int)


@pytest.mark.parametrize("missing", ["BOT_TOKEN", "MAIN_ADMIN_ID", "INSPECTOR_ID"])
def test_load_config_missing_variable_raises(monkeypatch, missing):
    set_env(monkeypatch, BOT_TOKEN="t", MAIN_ADMIN_ID="1", INSPECTOR_ID="2")
    monkeypatch.delenv(missing)

    with pytest.raises(ConfigError) as err:
        load_config()

    assert missing in str(err.value)


@pytest.mark.parametrize("name", ["MAIN_ADMIN_ID", "INSPECTOR_ID"])
def test_load_config_non_numeric_id_raises(monkeypatch, name):
    set_env(monkeypatch, BOT_TOKEN="t", MAIN_ADMIN_ID="1", INSPECTOR_ID="2")
    monkeypatch.setenv(name, "не-число")

    with pytest.raises(ConfigError) as err:
        load_config()

    assert name in str(err.value)


# ── Config ───────────────────────────────────────────────────────────

def test_config_is_immutable():
    cfg = Config(bot_token="t", main_admin_id=1, inspector_id=2)

    with pytest.raises(dataclasses.FrozenInstanceError):
        cfg.bot_token = "другой"


# ── get_config ───────────────────────────────────────────────────────────

def test_get_config_reads_environment_once(monkeypatch):
    set_env(monkeypatch, BOT_TOKEN="первый", MAIN_ADMIN_ID="1", INSPECTOR_ID="2")

    first = get_config()
    monkeypatch.setenv("BOT_TOKEN", "второй")

    assert get_config() is first
    assert get_config().bot_token == "первый"
