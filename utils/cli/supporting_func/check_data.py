import sys
from utils.misc.exceptions import CliInputError
import os
from pathlib import Path
from jsonschema import Draft202012Validator
from config_data.game_schema import SCHEMA


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


def check_file_exists(file_path: str) -> None:
    """
    Проверяет, существует ли файл по указанному пути.

    :param file_path: Путь к файлу
    :raises FileNotFoundError: Если файл не найден
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Файл по пути {file_path} не найден.")


def validate_media_files(data, game_root: Path) -> None:
    """
    Рекурсивно проходит по данным и проверяет,
    что все пути указывают на реально существующие файлы.
    """

    if isinstance(data, dict):
        for key, value in data.items():

            if key in {"audio", "image"}:
                file_path = game_root / value
                if not file_path.is_file():
                    raise FileNotFoundError(f"Файл не найден: {file_path}")

            else:
                validate_media_files(value, game_root)

    elif isinstance(data, list):
        for item in data:
            validate_media_files(item, game_root)
