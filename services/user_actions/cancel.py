from utils.decorators.log_exceptions import log_exceptions
from bot.loader import bot
from keyboards.inline_keyboards import objects_keyboard
from repositories.repositories import PlayerSessionRepository
from utils.decorators.with_context import with_context
import logging
from utils.misc.get_kwargs import get_kwargs


@with_context(include_player=True)
@log_exceptions()
def send_player_sessions_keyboard(**kwargs):
    chat_id, player = get_kwargs(("chat_id", "player"), kwargs)

    player_sessions = PlayerSessionRepository.filter(player=player, status="registered")
    if not player_sessions:
        bot.send_message(chat_id, "Нет записей. \nЧтобы записаться, введи /register")
        return
    bot.send_message(chat_id, f"Выбери игру, на которую нужно отменить запись:",
                     reply_markup=objects_keyboard(player_sessions, "cancel:"))


@with_context(include_player=True)
@log_exceptions()
def cancel_player_session(**kwargs):
    logging.info("\n\n___ call_cancel ___")

    data, chat_id, player, message_id = get_kwargs(("data", "chat_id", "player", "message_id"), kwargs)

    player_session_id = int(data.split(":")[1])
    player_session = PlayerSessionRepository.get(player_session_id=player_session_id)

    bot.edit_message_text(f"Отмена записи на {player_session.game_session}:", chat_id, message_id, reply_markup=None)

    player_session.delete_instance()

    bot.send_message(chat_id, "Запись успешно отменена.")
    logging.debug(f"{player}: отменил запись на игру {player_session.game_session}")
