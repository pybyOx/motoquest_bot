from utils.decorators.log_exceptions import log_exceptions
from loader import bot
from keyboards.inline_keyboards import objects_keyboard
from repositories.repositories import PlayerSessionRepository
from peewee import DoesNotExist, OperationalError
from utils.decorators.with_context import with_context
import logging
from utils.misc.get_kwargs import get_kwargs


@bot.message_handler(commands=["cancel"])
@log_exceptions()
@with_context()
def bot_cancel(**kwargs):
    message, user_id = get_kwargs(["message_or_callback", "user_id"], kwargs)
    send_player_sessions_keyboard(message)


@log_exceptions()
@with_context(include_player=True)
def send_player_sessions_keyboard(**kwargs):
    chat_id, player = get_kwargs(["chat_id", "player"], kwargs)

    player_sessions = PlayerSessionRepository.filter(player=player, status="registered")
    if not player_sessions:
        bot.send_message(chat_id, "Нет записей. \nЧтобы записаться, введи /register")
        return
    bot.send_message(chat_id, f"Выбери игру, на которую нужно отменить запись:",
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
        logging.error(f"При получении PlayerSession: {error}", exc_info=True)
        raise
    try:
        player_session.delete_instance()
    except (OperationalError, Exception) as error:
        logging.error(f"При удалении PlayerSession: {error}", exc_info=True)
        raise
    else:
        bot.send_message(chat_id, "Запись успешно отменена.")
        logging.debug(f"{player}: отменил запись на игру {player_session.game_session}")
