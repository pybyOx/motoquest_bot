from functools import wraps
import logging
from loader import bot
from utils.misc.get_kwargs import get_kwargs
from repositories.repositories import PlayerRepository
from states.states_game import ErrorStates
from config_data.config import ADMIN_IDS
from peewee import DoesNotExist
from utils.misc.exceptions import CreationError


def log_exceptions():
    """
    Декоратор централизованной обработки исключений.

    Назначение:
        Перехватывает любые необработанные исключения, возникшие внутри
        декорируемой функции, и переводит пользователя в безопасное состояние
        восстановления (error-flow).

    Основные задачи:
        - Централизованное логирование исключений с traceback.
        - Уведомление администратора о сбое.
        - Информирование пользователя о возникшей ошибке.
        - Очистка возможных «лишних» сообщений в чате.
        - Сохранение контекста выполнения функции для последующего восстановления.
        - Перевод пользователя в состояние ожидания исправления ошибки.

    Требования к декорируемой функции:
        Функция должна быть обёрнута декоратором with_context
        и получать следующие параметры в kwargs:
            - message_id (int)
            - user_id (int)
            - chat_id (int)
            - username (str | None)

    Поведение при возникновении исключения:
        1. Перехватывает любое исключение типа Exception.
        2. Извлекает служебные данные (message_id, user_id, chat_id, username).
        3. Получает текущее состояние пользователя.
        4. Логирует исключение с полным traceback.
        5. Отправляет уведомление администратору.
        6. Пытается удалить сообщения, отправленные после сообщения,
           вызвавшего ошибку (диапазон message_id + 1 … message_id + 9).
        7. Отправляет пользователю сообщение о временной ошибке.
        8. Получает или создаёт сущность Player.
        9. Сохраняет информацию о текущей функции и её аргументах
           (current_func) для механизма восстановления.
        10. Переводит пользователя в состояние ErrorStates.waiting_for_fix.
        11. Прерывает дальнейшее выполнение функции и возвращает None.

    Работа с исключениями:
        - Исключение НЕ пробрасывается дальше.
        - Выполнение декорируемой функции полностью останавливается.
        - Все последующие действия выполняются только после восстановления.

    Рекомендации по использованию:
        - Использовать как внешний (последний) декоратор для хендлеров.
        - Не перехватывать Exception внутри хендлеров без необходимости.
        - Обрабатывать внутри хендлеров только ожидаемые пользовательские
          и бизнес-сценарии.
        - Все неожиданные ошибки должны доходить до log_exceptions.

    Ограничения:
        - Декоратор не различает типы исключений — любое Exception считается аварийным.
        - Предназначен для использования в связке с FSM и recovery-механизмом.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                message_id, user_id, chat_id, username = get_kwargs(
                    ("message_id", "user_id", "chat_id", "username"), kwargs)

                logging.error(f"{user_id}:Исключение в {func.__name__}", exc_info=True)
                try:
                    bot.send_message(ADMIN_IDS[0], f"{user_id}: Исключение в {func.__name__}")
                    bot.send_message(chat_id, "Упс! Возникла ошибка. Мы уже исправляем 🛠️.\n "
                                              "Как только всё будет готово, ты продолжишь с того же места.")
                except Exception:
                    logging.error(f"Не удалось отправить сообщение администратору или игроку", exc_info=True)

                from telebot import TeleBot
                from telebot.apihelper import ApiTelegramException

                if isinstance(message_id, int):
                    for msg_id in range(message_id + 1, message_id + 10):
                        try:
                            bot.delete_message(chat_id, msg_id)
                        except (ApiTelegramException, Exception) as error:
                            logging.debug(f"При удалении сообщения {msg_id} : {error}")
                            continue

                try:
                    player = PlayerRepository.get(user_id=user_id)
                except DoesNotExist:
                    player = PlayerRepository.create(user_id=user_id, username=username)
                try:
                    current_state = bot.get_state(user_id, chat_id)
                    if current_state != ErrorStates.state(ErrorStates.waiting_for_fix):
                        PlayerRepository.update_instance(player, current_func={f"{func.__name__}": [args, kwargs]})
                    bot.set_state(user_id, ErrorStates.waiting_for_fix, chat_id)
                except Exception as e:
                    logging.critical(f"{user_id}: {e}"
                                     f"\n recovery-данные: "
                                     f"\ncurrent_func: {func.__name__}"
                                     f"\nargs: {args}"
                                     f"\nkwargs: {kwargs}",
                                     exc_info=True)

                return None
        return wrapper
    return decorator
