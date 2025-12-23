import logging
from loader import bot
from states.states_game import GameState
from keyboards.inline_keyboards import review_keyboard
from config_data.config import ADMIN_IDS
from utils.decorators.with_context import with_context
from utils.decorators.log_exceptions import log_exceptions
from utils.misc.get_kwargs import get_kwargs
from peewee import DoesNotExist
from utils.misc.exceptions import JSONError
from datetime import datetime
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from repositories.repositories import ClueRepository, UserPointProgressRepository
from keyboards.inline_keyboards import clue_keyboard


@bot.message_handler(state=GameState.waiting_for_answer)
@with_context(include_user_point_progress=True)
@log_exceptions()
def handle_user_answer(**kwargs) -> None:

    content_type, user_id, chat_id, player, current_point, user_point_progress, data = (get_kwargs(
        ("content_type", "user_id", "chat_id", "player", "current_point", "user_point_progress", "data"), kwargs))

    logging.info(f"\n\n___{player}: отправил ответ на задание точки {current_point} ___")

    admin_msg = (f"Ответ на точку {current_point} от {player}:\n"
                 f"(тип - {current_point.answer['type']}, ответ - {current_point.answer['text']})")
    keyboard = review_keyboard(user_point_progress.user_point_progress_id)

    if content_type == 'text':
        bot.send_message(ADMIN_IDS[0], admin_msg)
        bot.send_message(ADMIN_IDS[0], data, reply_markup=keyboard)
    elif content_type == 'photo':
        bot.send_photo(ADMIN_IDS[0], data[-1].file_id, caption=admin_msg, reply_markup=keyboard)
    else:
        bot.send_message(chat_id, "В качестве ответа пришлите, пожалуйста, текст или фото.")
        logging.warning(f"{player}: неверный тип ответа {content_type}")
        return

    bot.send_message(chat_id, "Ваш ответ получен. Ожидайте проверки.")
    logging.debug(f"{player}: ответ отправлен на проверку.")

    safe_set_state(user_id, GameState.waiting_for_review, chat_id)


@bot.message_handler(state=GameState.waiting_for_review)
@with_context()
@log_exceptions()
def handle_waiting_for_review(**kwargs) -> None:

    chat_id, user_id = get_kwargs(("chat_id", "user_id"), kwargs)

    bot.send_message(chat_id, "Ваш ответ отправлен на проверку. Ожидайте.")


@bot.callback_query_handler(func=lambda c: c.data.startswith(("answer_correct:", "answer_wrong:")))
@with_context()
@log_exceptions()
def call_review(**kwargs):
    logging.info(f"\n\n___ call_review ___")

    user_id, chat_id, message_id, data = (get_kwargs(("user_id", "chat_id", "message_id", "data"), kwargs))
    user_point_progress_id = int(data.split(":")[1])
    bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)

    user_point_progress = UserPointProgressRepository.get(user_point_progress_id=user_point_progress_id)

    player = user_point_progress.player_session.player
    after_solved: dict = user_point_progress.point.after_solved
    point = user_point_progress.point
    logging.debug(f"{player}: Получили UserPointProgress по id")

    if data.startswith("answer_correct:"):
        logging.info(f"\n\n___{player}: ответ верный.___")

        bot.send_message(chat_id, "Верно")

        UserPointProgressRepository.update_instance(instance=user_point_progress,
                                                    finished_at=datetime.now(),
                                                    is_finished=True)

        logging.debug("UserPointProgress успешно обновлен.")
        logging.info(f"{player}: Время прохождения точки {point}: {user_point_progress.time}.")

        bot.send_message(player.user_id, after_solved["value"])
        bot.send_message(player.user_id, after_solved["facts"])

        logging.debug(f"{player}:Отправлен ответ на правильное решение точки {point}.")

        bot.send_message(player.user_id, "Едем дальше?",
                         reply_markup=InlineKeyboardMarkup().add(
                             InlineKeyboardButton("Вперёд!", callback_data="choice_location")))
        logging.debug(f"{player}: отправлена клавиатура с оставшимися локациями.")

        bot.delete_state(player.user_id)

    if data.startswith("answer_wrong:"):
        logging.info(f"\n\n___{player}: ответ неверный.___")

        bot.send_message(chat_id, "Неверно")

        safe_set_state(player.user_id, GameState.waiting_for_answer, player.user_id)

        bot.send_message(player.user_id, "\u274C Ответ неверный. Попробуйте ещё раз или воспользуйтесь подсказкой.",
                         reply_markup=clue_keyboard(3 - user_point_progress.clues_used))
        logging.debug(f"{player}: отправлена клавиатура с подсказками.")


@bot.callback_query_handler(func=lambda call: call.data == "get_clue")
@with_context(include_user_point_progress=True)
@log_exceptions()
def call_get_clue(**kwargs):
    logging.info(f"\n\n___ call_get_clue ___")

    message_id, player, chat_id, current_point, user_point_progress, clues_left = (get_kwargs(
        ("message_id", "player", "chat_id", "current_point", "user_point_progress", "clues_left"), kwargs))

    logging.info(f"{player}: воспользовался подсказкой.")
    bot.delete_message(chat_id=chat_id, message_id=message_id)

    clues = ClueRepository.filter(point=current_point)
    clue = list(clues)[-clues_left]

    bot.send_message(chat_id, f"Подсказка №{clue.order}:\n{clue.text}")
    logging.debug(f"{player}: подсказка отправлена")

    if user_point_progress.clues_used < 3:
        new_value = user_point_progress.clues_used + 1
        UserPointProgressRepository.update_instance(user_point_progress, clues_used=new_value)


def safe_set_state(user_id, state, chat_id):
    logging.debug(f"\n\nМеняем состояние {user_id}, {chat_id}")
    before = bot.get_state(user_id, chat_id)
    bot.set_state(user_id, state, chat_id)
    after = bot.get_state(user_id, chat_id)
    logging.debug(f"{user_id}: состояние изменилось {before} → {after}")
