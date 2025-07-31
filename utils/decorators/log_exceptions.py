from functools import wraps
import logging
from loader import bot
from utils.misc.get_kwargs import get_kwargs
from repositories.repositories import PlayerRepository
from states.states_game import ErrorStates
from config_data.config import ADMIN_IDS
from peewee import DoesNotExist


def log_exceptions(level=logging.CRITICAL):
    """Декоратор для логирования всех исключений с traceback."""
    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                message_id, user_id, chat_id, username = get_kwargs(
                    ["message_id", "user_id", "chat_id", "username"], kwargs)
                current_state = bot.get_state(user_id, chat_id)
                logging.error(f"{user_id}:Исключение в {func.__name__}", exc_info=True)
                bot.send_message(ADMIN_IDS[0], f"{user_id}:Исключение в {func.__name__}")

                from telebot import TeleBot
                from telebot.apihelper import ApiTelegramException

                for msg_id in range(message_id + 1, message_id + 10):
                    try:
                        bot.delete_message(chat_id, msg_id)
                    except (ApiTelegramException, Exception) as error:
                        logging.error(f"При удалении сообщения {msg_id} : {error}")
                        continue

                bot.send_message(chat_id, "Упс! Возникла ошибка. Мы уже исправляем 🛠️.\n "
                                          "Как только всё будет готово, ты продолжишь с того же места.")
                try:
                    player = PlayerRepository.get(user_id=user_id)
                except DoesNotExist:
                    player = PlayerRepository.create(user_id=user_id, username=username)
                if current_state != "ErrorStates.waiting_for_fix":
                    PlayerRepository.update_instance(player, current_func={f"{func.__name__}": [args, kwargs]})

                bot.set_state(user_id, ErrorStates.waiting_for_fix, chat_id)

                return None
        return wrapper
    return decorator
