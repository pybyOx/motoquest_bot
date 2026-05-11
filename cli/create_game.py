from __future__ import annotations
import logging
import json
import sys
from json import JSONDecodeError
from pathlib import Path

from core.exceptions import AlreadyExistsError, CliInputError
from core.utils.check_data import (get_data_from_argv,
                                   validate_game_json, validate_media_files)
from core.container import get_container


container = get_container()
game_info_repo = container.game_info_repo
point_repo = container.point_repo
clue_repo = container.clue_repo


def create_game(file_path: str) -> None:
    logging.info("___Создание GameInfo___")

    game_info = None

    try:
        file_path = Path(file_path)
        if not file_path.is_file():
            raise FileNotFoundError(f"Файл не найден: {file_path}")

    except (CliInputError, IndexError, FileNotFoundError) as error:
        logging.error(f"При получении пути к файлу: {error}", exc_info=True)
        sys.exit(1)
    else:
        logging.debug(f"cli-команда введена корректно. Файл найден.")

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            game_data = json.load(file)

    except (JSONDecodeError, UnicodeDecodeError) as error:
        logging.error(f"Ошибка чтения JSON-файла: {error}", exc_info=True)
        sys.exit(1)
    else:
        logging.debug("Данные из JSON-файла успешно извлечены.")

    try:
        validate_game_json(data=game_data)
        validate_media_files(game_data, Path(file_path).parent)
    except (ValueError, FileNotFoundError) as error:
        logging.error(f"Ошибка в данных игры: {error}")
        sys.exit(1)
    else:
        logging.debug("JSON и файлы прошли валидацию.")

    try:
        game_info = game_info_repo.create(dict(
            title=game_data["title"],
            slug=game_data["slug"],
            finish=game_data["finish"]
        ))
        for point_data in game_data["points"]:
            point = point_repo.create(dict(
                title=point_data["title"],
                location=point_data["location"],
                task=point_data["task"],
                answer=point_data["answer"],
                after_solved=point_data["after_solved"],
                game_info=game_info
            ))
            for i, clue_text in enumerate(point_data["clues"], start=1):
                clue_repo.create(dict(
                    point=point,
                    text=clue_text,
                    order=i
                ))

    except AlreadyExistsError as error:
        logging.error(f"Ошибка при создании игры: {error}")
        if game_info:
            game_info_repo.delete_by_id(id == game_info.id)
        sys.exit(1)
    else:
        logging.info(f"Информация о игре '{game_info}' успешно занесена в базу данных.")


if __name__ == "__main__":
    """
    Пример использования:
    python -m cli.create_game games_data/way_of_the_dragon/game_dragon.json
    """
    path = get_data_from_argv(length=2, index=1)
    create_game(path)
