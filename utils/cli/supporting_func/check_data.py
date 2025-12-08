import sys
from utils.misc.exceptions import CliInputError, JSONError
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
    Проверяет наличие обязательных ключей в словаре и то, что их значения непустые.

    :param required_keys: Множество ключей, которые должны присутствовать.
    :param data: Словарь для проверки.
    :raises KeyError: Если ключ отсутствует.
    :raises ValueError: Если значение ключа пустое (None, пустая строка/список/словарь).
    """

    missing_keys = required_keys.difference(data.keys())
    if missing_keys:
        raise KeyError(f"В словаре отсутствуют ключи: {', '.join(missing_keys)}")

    for key in required_keys:
        value = data[key]
        if value is None:
            raise ValueError(f"В словаре отсутствует значение ключа '{key}'")

        if isinstance(value, (str, list, dict, tuple)) and not value:
            raise ValueError(f"Значение ключа '{key}' не может быть пустым")


def is_correct_data_from_json(data: dict):
    """Проверяет корректность данных, извлеченных из json-файла игры.
    :param data: Словарь, подлежащий проверке.
    :raises JSONError: Ошибка в данных json-файла"""
    try:
        require_keys({"title", "finish", "points"}, data)

        if not isinstance(data["title"], str) or not data["title"].strip():
            raise ValueError(f"Некорректные данные: Поле 'title' должно быть непустой строкой.")

        points = data["points"]
        if not isinstance(points, dict) or not points:
            raise ValueError(f"Некорректные данные: поле 'points' должно быть непустым словарем.")

        for point_name, point_data in points.items():
            if not isinstance(point_name, str) or not point_name.strip():
                raise ValueError("Некорректные данные: Название точки должно быть непустой строкой.")
            if not isinstance(point_data, dict) or not point_data:
                raise ValueError(f"Некорректные данные: points[{point_name}] должно быть непустым словарем.")

            require_keys({"location", "task", "answer", "clues", "after_solved"}, point_data)

            for key, value in point_data.items():

                if key == "clues":
                    if not isinstance(value, list):
                        raise TypeError(f"{point_name}[clues] должен быть списком.")

                    if len(value) != 3:
                        raise ValueError(f"Некорректные данные: {point_name}[clues] должен содержать 3 подсказки.")

                    if not all(isinstance(clue, str) for clue in value):
                        raise TypeError(f"{point_name}[clues] должен содержать строки.")

                else:
                    if not isinstance(value, dict):
                        raise TypeError(f"{point_name}[{key}] должен быть словарем.")

                    if key == "location":
                        require_keys({"link"}, value)

                    elif key in {"task", "after_solved"}:
                        require_keys({"text"}, value)

                    elif key == "answer":
                        require_keys({"type", "value"}, value)

                        for attr in {"type", "value"}:
                            if not isinstance(value[attr], str):
                                raise TypeError(f"{point_name}[answer][{attr}] должен быть строкой.")

                        if value["type"] not in ["text", "photo"]:
                            raise ValueError(f"Некорректные данные:{point_name}[answer][type] должен быть 'text'/'photo'")

                if "text" in value:
                    if not isinstance(value["text"], str):
                        raise TypeError(f"{point_name}[{key}][text] должно быть строкой.")

                if "facts" in value:
                    if not isinstance(value["facts"], list):
                        raise TypeError(f"{point_name}[{key}][facts] должен быть списком.")
                    if not all(isinstance(fact, str) for fact in value["facts"]):
                        raise TypeError(f"{point_name}[{key}][facts] должен содержать строки.")

                if "link" in value:
                    if not is_map_link(value["link"]):
                        raise ValueError(f"Некорректная ссылка: {point_name}[{key}][link]")

                for attr in {"image", "voice"}:
                    if attr in value:
                        if not isinstance(value[attr], str):
                            raise TypeError(f"{point_name}[{key}][{attr}] должен быть строкой.")
                        check_file_exists(value[attr])

        if not isinstance(data["finish"], dict):
            raise TypeError(f"Поле 'finish' должно быть словарем.")
        require_keys({"text", "link"}, data["finish"])

        if not isinstance(data["finish"]["text"], str):
            raise TypeError(f"[finish][text] должно быть строкой.")

        if not is_map_link(data["finish"]["link"]):
            raise ValueError(f"Некорректная ссылка в [finish][link]")

    except (KeyError, FileNotFoundError, ValueError, TypeError) as e:
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
