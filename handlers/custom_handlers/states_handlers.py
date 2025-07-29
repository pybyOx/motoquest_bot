import logging
from loader import bot
from states.states_game import GameState
from keyboards.inline.keyboards import review_keyboard
from config_data.config import ADMIN_IDS
from utils.decorators.with_context import with_context
from utils.decorators.log_exceptions import log_exceptions
from utils.misc.get_kwargs import get_kwargs
from telebot.types import Message
from telebot.apihelper import ApiTelegramException
from peewee import DoesNotExist
from utils.misc.exceptions import JSONError
from datetime import datetime
from utils.choice_location import send_choice_location
from repositories.repositories import ClueRepository, UserPointProgressRepository
from keyboards.inline.keyboards import clue_keyboard


@bot.message_handler(state=GameState.waiting_for_answer, content_types=['text', 'photo'])
@log_exceptions()
@with_context(include_user_point_progress=True)
def handle_user_answer(**kwargs) -> None:

    message_or_callback, user_id, chat_id, player, current_point, user_point_progress = (
        get_kwargs(["message_or_callback", "user_id", "chat_id", "player", "current_point", "user_point_progress"],
                   kwargs))

    logging.info(f"\n\n___{player}: отправил ответ на задание точки {current_point} ___")

    try:
        admin_msg = (f"Ответ на точку {current_point} от {player}:\n"
                     f"(тип - {current_point.answer['type']}, ответ - {current_point.answer['value']})")

        keyboard = review_keyboard(user_point_progress.user_point_progress_id)

        if message_or_callback.content_type == 'text':
            bot.send_message(ADMIN_IDS[0], admin_msg)
            bot.send_message(ADMIN_IDS[0], message_or_callback.text, reply_markup=keyboard)
        elif message_or_callback.content_type == 'photo':
            bot.send_photo(ADMIN_IDS[0], message_or_callback.photo[-1].file_id, caption=admin_msg, reply_markup=keyboard)
        else:
            bot.send_message(chat_id, "В качестве ответа пришлите текст или фото.")
            raise TypeError(f"{player}: отправил ответ неверного формата {message_or_callback.content_type}")

    except (TypeError, ValueError, AttributeError, KeyError, IndexError, ApiTelegramException, Exception) as error:
        logging.error(f"При отправлении ответа админу: {error}", exc_info=True)
        raise
    else:
        bot.send_message(chat_id, "Ответ получен. Ожидайте проверки.")
        logging.debug(f"{player}: ответ отправлен на проверку.")

        bot.set_state(user_id, GameState.waiting_for_review, chat_id)
        logging.info(f"\n\n___{player}: waiting_for_review___")


@bot.message_handler(state=GameState.waiting_for_review)
@log_exceptions()
@with_context()
def handle_waiting_for_review(**kwargs) -> None:
    chat_id = get_kwargs(["user_id"], kwargs)[0]
    bot.send_message(chat_id, "Ваш ответ отправлен на проверку. Ожидайте.")


@bot.callback_query_handler(func=lambda c: c.data.startswith(("answer_correct:", "answer_wrong:")))
@log_exceptions()
@with_context()
def call_review(**kwargs):
    logging.info(f"\n\n___ call_review ___")

    user_id, chat_id, call = (get_kwargs(["user_id", "chat_id", "message_or_callback"], kwargs))
    user_point_progress_id = int(call.data.split(":")[1])
    bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)

    try:
        user_point_progress = UserPointProgressRepository.get(user_point_progress_id=user_point_progress_id)
    except (DoesNotExist, Exception) as error:
        logging.error(f"При получении UserPointProgress: {error}", exc_info=True)
        raise

    player = user_point_progress.player_session.player
    after_solved: dict = user_point_progress.point.after_solved
    point = user_point_progress.point
    player_session = user_point_progress.player_session
    logging.debug(f"{player}: Получили UserPointProgress по id")

    if call.data.startswith("answer_correct:"):
        logging.info(f"\n\n___{player}: ответ верный.___")
        bot.send_message(chat_id, "Верно")
        try:
            UserPointProgressRepository.update_instance(instance=user_point_progress,
                                                        finished_at=datetime.now(),
                                                        is_finished=True)
        except (ValueError, Exception) as error:
            logging.error(f"Ошибка обновления UserPointProgress: {error}")

        else:
            logging.debug("UserPointProgress успешно обновлен.")
            logging.info(f"{player}: Время прохождения точки {point}: {user_point_progress.time}.")

        try:
            bot.send_message(player.user_id, after_solved["value"])
            bot.send_message(player.user_id, after_solved["facts"])

        except (KeyError, Exception) as error:
            logging.error(f"{player}:При отправке after_solved точки {point}: {error}", exc_info=True)
            raise

        logging.debug(f"{player}:Отправлен ответ на правильное решение точки {point}.")

        send_choice_location(player_session=player_session)
        logging.debug(f"{player}: отправлена клавиатура с оставшимися локациями.")

        bot.delete_state(player.user_id)

    if call.data.startswith("answer_wrong:"):
        logging.info(f"\n\n___{player}: ответ неверный.___")
        bot.send_message(chat_id, "Неверно")
        bot.set_state(player.user_id, GameState.waiting_for_answer, chat_id)
        logging.info(f"{player}: waiting_for_answer")

        bot.send_message(player.user_id, "\u274C Ответ неверный. Попробуйте ещё раз или воспользуйтесь подсказкой.",
                         reply_markup=clue_keyboard(3 - user_point_progress.clues_used))
        logging.debug(f"{player}: отправлена клавиатура с подсказками.")


@bot.callback_query_handler(func=lambda call: call.data == "get_clue")
@log_exceptions()
@with_context(include_user_point_progress=True)
def call_get_clue(**kwargs):
    logging.info(f"\n\n___ call_get_clue ___")

    call, player, chat_id, current_point, user_point_progress, clues_left = (get_kwargs(
        ["message_or_callback", "player", "chat_id", "current_point", "user_point_progress", "clues_left"], kwargs))
    logging.info(f"{player}: воспользовался подсказкой.")
    bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)

    try:
        clues = ClueRepository.filter(point=current_point)
        if clues:
            clue = list(clues)[-clues_left]
        else:
            raise JSONError(f"Не найдено подсказок для {current_point}")
    except (JSONError, IndexError, Exception) as error:
        logging.error(f"{player}:Ошибка получения подсказок: {error}", exc_info=True)
        raise

    bot.send_message(chat_id, f"Подсказка №{clue.order}:\n{clue.text}")
    logging.debug(f"{player}: подсказка отправлена")

    if user_point_progress.clues_used < 3:
        new_value = user_point_progress.clues_used + 1
        UserPointProgressRepository.update_instance(user_point_progress, clues_used=new_value)
