import sys
from core.exceptions import CliInputError
import logging
from pathlib import Path
from jsonschema import Draft202012Validator
from config_data.game_schema import SCHEMA
import requests
from datetime import datetime, UTC
from zoneinfo import ZoneInfo


def get_data_from_argv(length: int, index: int) -> str:
    """
    Проверяет, что cli-команда введена корректно и возвращает аргумент, соответствующий переданному индексу.

    :param length: Количество аргументов, переданных cli-командой.
    :param index: Индекс нужного аргумента в sys.argv.
    :return: Аргумент, соответствующий переданному индексу.
    :raises CliInputError: Некорректный ввод команды.
    """
    if len(sys.argv) < length:
        raise CliInputError(f"Ошибка ввода cli-команды. Аргументов меньше {length}.")

    data = sys.argv[index]

    return data


def is_url_accessible(url: str, timeout: float = 5.0) -> bool:
    try:
        response = requests.get(url, allow_redirects=True, timeout=timeout, stream=True)
        return 200 <= response.status_code < 400
    except requests.RequestException:
        return False


def parse_user_datetime_to_utc(
    date_str: str,
    user_timezone: str,
    fmt: str = "%d.%m.%Y %H:%M"
) -> datetime:

    local_dt = datetime.strptime(date_str, fmt)

    return (
        local_dt
        .replace(tzinfo=ZoneInfo(user_timezone))
        .astimezone(UTC)
        .replace(tzinfo=None)
    )


def validate_game_json(data: dict):
    """Проверяет корректность данных, извлеченных из json-файла игры.
    :param data: Словарь, подлежащий проверке.
    :raises ValueError: Ошибка в данных json-файла"""
    validator = Draft202012Validator(SCHEMA)
    errors = list(validator.iter_errors(data))

    if errors:
        for error in errors:
            print(error.message)
        raise ValueError("JSON не прошёл валидацию")


def validate_media_files(data, game_root: Path) -> None:
    """
    Рекурсивно проходит по данным и проверяет,
    что все пути указывают на реально существующие файлы,
    что ссылки на карты рабочие.
    """

    if isinstance(data, dict):
        for key, value in data.items():

            if key in {"audio", "image"}:
                file_path = game_root / value
                if not file_path.is_file():
                    raise FileNotFoundError(f"Файл не найден: {file_path}")
            elif key == "link":
                if not is_url_accessible(value):
                    logging.warning(f"Ссылка на карту может быть недоступна: {value} ")

            else:
                validate_media_files(value, game_root)

    elif isinstance(data, list):
        for item in data:
            validate_media_files(item, game_root)
