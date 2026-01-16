import utils.misc.logger
import logging
from loader import bot
import handlers  # noqa: F401  # регистрация хендлеров
from database.database_model import create_models, setup_db, close_db
from telebot.custom_filters import StateFilter
import atexit


if __name__ == "__main__":
    logging.debug("Bot starting")
    setup_db()
    create_models()
    bot.add_custom_filter(StateFilter(bot))
    atexit.register(close_db)
    bot.infinity_polling()
