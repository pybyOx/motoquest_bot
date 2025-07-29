from telebot.types import Message
from keyboards.inline.keyboards import objects_keyboard
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
def bot_register(message: Message):
    send_sessions_keyboard(message.chat.id)


def send_sessions_keyboard(chat_id: int):
    """
    Ищет активные игровые сессии.

    Если находит, отправляет клавиатуру с играми для записи;
    иначе отправляет сообщение о том, что активных сессий нет.
    """

    game_sessions = GameSessionRepository.filter(finished=False)
    if not game_sessions:
        bot.send_message(chat_id, "Нет активных игровых сессий.")
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
        bot.send_message(chat_id, "Ошибка получения данных. Пожалуйста, обратитесь к организатору.")
        logging.critical(f"При получении GameSession: {error}", exc_info=True)
        return

    try:
        PlayerSessionRepository.create(player=player, game_session=game_session)
    except CreationError as error:
        bot.send_message(chat_id, "Ошибка записи на игру. Пожалуйста, обратитесь к организатору.")
        logging.critical(f"При создании PlayerSession: {error}", exc_info=True)
    except AlreadyExistsError as error:
        bot.send_message(chat_id, "Вы уже записаны на эту игру.")
        logging.error(f"При записи на игру: {error}", exc_info=True)
    else:
        bot.send_message(chat_id, f"Отлично! Вы записаны на игру {game_session}!\n"
                                  f"Место встречи: {game_session.location}", parse_mode="Markdown")

        logging.debug(f"{player}: записался на игру {game_session}")
