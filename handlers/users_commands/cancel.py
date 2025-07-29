from utils.decorators.log_exceptions import log_exceptions
from loader import bot
from telebot.types import Message
from keyboards.inline.keyboards import objects_keyboard
from repositories.repositories import PlayerSessionRepository, PlayerRepository
from peewee import DoesNotExist, OperationalError
from utils.decorators.with_context import with_context
import logging
from utils.misc.get_kwargs import get_kwargs


@bot.message_handler(commands=["cancel"])
@log_exceptions()
@with_context()
def bot_cancel(**kwargs):
    user_id = get_kwargs(["user_id"], kwargs)[0]
    send_player_sessions_keyboard(user_id)


@log_exceptions()
@with_context()
def send_player_sessions_keyboard(user_id: int):
    try:
        player = PlayerRepository.get(user_id=user_id)
    except DoesNotExist:
        bot.send_message(user_id, "Сначала зарегистрируйся, нажав команду /start")
        return

    player_sessions = PlayerSessionRepository.filter(player=player, status="registered")
    if not player_sessions:
        bot.send_message(user_id, "Нет записей. Чтобы записаться, введи /register")
        return
    bot.send_message(user_id, f"Выбери игру, на которую нужно отменить запись:",
                     reply_markup=objects_keyboard(player_sessions, "cancel:"))


@bot.callback_query_handler(func=lambda c: c.data.startswith("cancel:"))
@log_exceptions()
@with_context(include_player=True)
def call_cancel(**kwargs):
    logging.info("\n\n___ call_cancel ___")

    call, chat_id, player = get_kwargs(["message_or_callback", "chat_id", "player"], kwargs)
    player_session_id = int(call.data.split(":")[1])

    bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)

    try:
        player_session = PlayerSessionRepository.get(player_session_id=player_session_id)
    except DoesNotExist as error:
        bot.send_message(chat_id, "Ошибка отмены записи. Пожалуйста, обратитесь к организатору.")
        logging.error(f"При получении PlayerSession: {error}", exc_info=True)
        return
    try:
        player_session.delete_instance()
    except (OperationalError, Exception) as error:
        bot.send_message(chat_id, "Ошибка отмены записи. Пожалуйста, обратитесь к организатору.")
        logging.error(f"При удалении PlayerSession: {error}", exc_info=True)
        return
    else:
        bot.send_message(chat_id, "Запись успешно отменена.")
        logging.debug(f"{player}: отменил запись на игру {player_session.game_session}")
