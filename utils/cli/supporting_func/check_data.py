import sys
from utils.misc.exceptions import CliInputError
from utils.misc.exceptions import JSONError
import os
import re


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


def require_keys(required_keys: set, data: dict):
    """
    Проверяет наличие ключей в словаре.

    :param required_keys: Ключи, которые должны быть в словаре.
    :param data: Словарь, который нужно проверить.
    :raises KeyError: Если в словаре отсутствуют необходимые ключи.
    """

    missing_keys = required_keys - data.keys()
    if missing_keys:
        raise KeyError(f"В словаре отсутствуют ключи: {', '.join(missing_keys)}")


def is_correct_data_from_json(data: dict, required_keys: set):
    """Проверяет корректность данных, извлеченных из json-файла игры.
    :param data: Словарь, подлежащий проверке.
    :param required_keys: Ключи, которые должны быть в словаре.
    :raises JSONError: Ошибка в данных json-файла"""
    try:
        require_keys(required_keys=required_keys, data=data)
        for key in data.keys():
            if key == "location":
                if not is_map_link(data[key]):
                    raise ValueError(f"Некорректная ссылка на локацию в {key}")
            if isinstance(data[key], dict):
                if "location" in data[key]:
                    if not is_map_link(data[key]["location"]):
                        raise ValueError(f"Некорректная ссылка на локацию в {key}")
                if "photo" in data[key]:
                    check_file_exists(data[key]["photo"])
                if "voice" in data[key]:
                    check_file_exists(data[key]["voice"])
            if isinstance(data[key], list):
                for obj in data[key]:
                    if isinstance(obj, dict):
                        is_correct_data_from_json(obj, {"title", "location", "task", "answer", "clues", "after_solved"})
    except (KeyError, FileNotFoundError, ValueError) as e:
        raise JSONError(f"{e}")


def check_file_exists(file_path: str) -> None:
    """
    Проверяет, существует ли файл по указанному пути.

    :param file_path: Путь к файлу
    :raises FileNotFoundError: Если файл не найден
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Файл по пути {file_path} не найден.")


def is_map_link(url: str) -> bool:
    """Проверяет, является ли URL ссылкой на карту (Google, Yandex, OSM и др.)."""
    if not isinstance(url, str):
        return False

    url = url.strip()

    map_patterns = [r'^https:\/\/(www\.)?google\.[a-z.]+\/maps\/.+',
                    r'^https:\/\/maps\.google\.[a-z.]+\/\?q=.+',
                    r'^https:\/\/(yandex|maps\.yandex)\.[a-z.]+\/maps\/.+',
                    r'^https:\/\/(www\.)?openstreetmap\.org\/.+',
                    r'^https:\/\/www\.bing\.com\/maps\/.+',
                    r'^https:\/\/t\.me\/addlocation\/.+']

    return any(re.match(pattern, url) for pattern in map_patterns)
