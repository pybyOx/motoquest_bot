from keyboards.inline_keyboards import objects_keyboard
from loader import bot
from peewee import DoesNotExist
from utils.decorators.log_exceptions import log_exceptions
from utils.decorators.with_context import with_context
import logging
from utils.misc.exceptions import CreationError, AlreadyExistsError
from utils.misc.get_kwargs import get_kwargs
from repositories.repositories import GameSessionRepository, PlayerSessionRepository
from utils.misc.escape_markdown import escape_markdown
from telebot.types import Message


@bot.message_handler(commands=["register"])
def bot_register(message: Message):
    send_sessions_keyboard(message)


@with_context()
@log_exceptions()
def send_sessions_keyboard(**kwargs):
    """
    Ищет активные игровые сессии.

    Если находит, отправляет клавиатуру с играми для записи;
    иначе отправляет сообщение о том, что активных сессий нет.
    """
    logging.info("\n\n___ send_sessions_keyboard ___")
    chat_id = kwargs['chat_id']

    game_sessions = GameSessionRepository.filter(finished=False)
    if not game_sessions:
        bot.send_message(chat_id, "Нет игр для записи.")
        return

    bot.send_message(chat_id, f"Выбери игру, на которую хочешь записаться:",
                     reply_markup=objects_keyboard(game_sessions, "register:"))


@bot.callback_query_handler(func=lambda c: c.data.startswith("register:"))
@with_context(include_player=True)
@log_exceptions()
def call_register(**kwargs):
    logging.info("\n\n___ call_register ___")

    data, chat_id, player, message_id = get_kwargs(("data", "chat_id", "player", "message_id"), kwargs)
    session_id = int(data.split(":")[1])

    game_session = GameSessionRepository.get(session_id=session_id)
    bot.edit_message_text(f"Запись на {game_session}:", chat_id, message_id, reply_markup=None)

    try:
        PlayerSessionRepository.create(player=player, game_session=game_session)
    except AlreadyExistsError:
        bot.send_message(chat_id, "Вы уже записаны на эту игру.")
        return

    bot.send_message(chat_id, f"Вы успешно записаны! 🗺️ {game_session.location}",
                     parse_mode="HTML", disable_web_page_preview=True)

    logging.debug(f"{player}: записался на игру {game_session}")
