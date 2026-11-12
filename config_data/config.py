import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

from core.exceptions import ConfigError


BASE_DIR = Path(__file__).resolve().parent.parent
GAMES_DATA_DIR = BASE_DIR / "games_data"


def _require(name: str) -> str:
    """Возвращает значение переменной окружения или падает с понятной ошибкой"""
    value = os.getenv(name)
    if value is None:
        raise ConfigError(f"Не задана обязательная переменная окружения {name}")
    return value


def _require_int(name: str) -> int:
    """То же самое, но значение должно быть целым числом"""
    value = _require(name)
    try:
        return int(value)
    except ValueError as err:
        raise ConfigError(
            f"Переменная окружения {name} должна быть целым числом, получено: {value!r}"
        ) from err


@dataclass(frozen=True)
class Config:
    bot_token: str
    database_url: str
    main_admin_id: int
    inspector_id: int


def load_config() -> Config:
    """Читает окружение и собирает Config"""
    load_dotenv()
    return Config(
        bot_token=_require("BOT_TOKEN"),
        database_url=_require("DATABASE_URL"),
        main_admin_id=_require_int("MAIN_ADMIN_ID"),
        inspector_id=_require_int("INSPECTOR_ID"),
    )


@lru_cache
def get_config() -> Config:
    """Ленивый доступ к конфигу: окружение читается один раз, при первом обращении"""
    return load_config()
