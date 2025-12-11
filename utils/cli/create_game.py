import json
import sys
from utils.misc.exceptions import CreationError, AlreadyExistsError, CliInputError
from utils.cli.supporting_func.check_data import (get_data_from_argv, check_file_exists,
                                                  validate_game_json, validate_media_files)
import logging
from json import JSONDecodeError
from repositories.repositories import GameInfoRepository, PointRepository, ClueRepository
from pathlib import Path


if __name__ == "__main__":
    """
    Пример использования:
    python -m utils.cli.create_game games_data/way_of_the_dragon/game_dragon.json
    """
    logging.info("\n\n___Создание GameInfo___")

    game_info = None

    try:
        file_path = get_data_from_argv(length=2, index=1)
        check_file_exists(file_path)

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
        game_info = GameInfoRepository.create(title=game_data["title"],
                                              finish=game_data["finish"])
        for point_data in game_data["points"]:
            point = PointRepository.create(title=point_data["title"],
                                           location=point_data["location"],
                                           task=point_data["task"],
                                           answer=point_data["answer"],
                                           after_solved=point_data["after_solved"],
                                           game_info=game_info)
            for i, clue_text in enumerate(point_data["clues"], start=1):
                ClueRepository.create(point=point, text=clue_text, order=i)

    except (CreationError, AlreadyExistsError) as error:
        logging.error(f"Ошибка при создании игры: {error}")
        if game_info:
            GameInfoRepository.delete_instance(game_info)
        sys.exit(1)
    else:
        logging.info(f"Информация о игре '{game_info}' успешно занесена в базу данных.")
