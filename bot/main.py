import logging
from database.lifecycle import create_models, setup_db, close_db
from cli.create_game import create_game
from cli.set_admin import set_admin
from cli.recover_user import recover_user
import atexit
from core.container import get_container

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",  # Формат логов
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("bot.log", encoding='utf-8'),
              logging.StreamHandler()
              ])

# Подавить лишние отладочные логи
logging.getLogger('peewee').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)


import handlers  # noqa: F401  # регистрация хендлеров


if __name__ == "__main__":
    logging.debug("Bot starting")
    setup_db()
    create_models()

    # create_game(file_path="games_data/way_of_the_dragon/game_dragon.json")
    # set_admin(395578226)
    # recover_user(795176222)
    # recover_user(395578226)

    atexit.register(close_db)
    get_container().bot.infinity_polling()


