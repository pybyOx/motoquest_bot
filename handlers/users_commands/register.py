from keyboards.inline_keyboards import objects_keyboard
from loader import bot
from peewee import DoesNotExist
from utils.decorators.log_exceptions import log_exceptions
from utils.decorators.with_context import with_context
import logging
from utils.misc.exceptions import CreationError, AlreadyExistsError
from utils.misc.get_kwargs import get_kwargs
from repositories.repositories import GameSessionRepository, PlayerSessionRepository


@bot.message_handler(commands=["register"])
@log_exceptions()
@with_context()
def bot_register(**kwargs):
    send_sessions_keyboard(kwargs['message_or_callback'])


@log_exceptions()
@with_context()
def send_sessions_keyboard(**kwargs):
    """
    Ищет активные игровые сессии.

    Если находит, отправляет клавиатуру с играми для записи;
    иначе отправляет сообщение о том, что активных сессий нет.
    """
    chat_id = kwargs['chat_id']

    game_sessions = GameSessionRepository.filter(finished=False)
    if not game_sessions:
        bot.send_message(chat_id, "Нет игр для записи.")
        return

    bot.send_message(chat_id, f"Выбери игру, на которую хочешь записаться:",
                     reply_markup=objects_keyboard(game_sessions, "register:"))


@bot.callback_query_handler(func=lambda c: c.data.startswith("register:"))
@log_exceptions()
@with_context(include_player=True)
def call_register(**kwargs):
    logging.info("\n\n___ call_register ___")

    call, chat_id, player = get_kwargs(["message_or_callback", "chat_id", "player"], kwargs)
    session_id = int(call.data.split(":")[1])

    bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)

    try:
        game_session = GameSessionRepository.get(session_id=session_id)
    except DoesNotExist as error:
        logging.error(f"При получении GameSession: {error}", exc_info=True)
        raise

    try:
        PlayerSessionRepository.create(player=player, game_session=game_session)
    except CreationError as error:
        logging.error(f"При создании PlayerSession: {error}", exc_info=True)
        raise
    except AlreadyExistsError:
        bot.send_message(chat_id, "Вы уже записаны на эту игру.")

    bot.send_message(chat_id, f"Отлично! Вы записаны на игру {game_session}!\n"
                              f"Место встречи: {game_session.location}", parse_mode="Markdown")

    logging.debug(f"{player}: записался на игру {game_session}")
