from loader import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiTelegramException
from keyboards.inline_keyboards import objects_keyboard
from utils.decorators.log_exceptions import log_exceptions
from utils.decorators.with_context import with_context
import logging
from utils.misc.get_kwargs import get_kwargs
from repositories.repositories import (PointRepository, PlayerSessionRepository, UserPointProgressRepository)
from states.states_game import GameState
from datetime import datetime, UTC
from handlers.custom_handlers.states_handlers import safe_set_state


@bot.callback_query_handler(func=lambda callback: callback.data == "choice_location")
@with_context(include_player_session=True)
@log_exceptions()
def send_choice_location(**kwargs) -> None:
    """Проверяет наличие незавершенных UserPointProgress игровой сессии и присылает клавиатуру с кнопками:

    - если есть: {Название локации}, callback_data="select_point: {id Point}"
    - если нет: {" 🎉"}, callback_data="finish"
    """
    logging.info("\n\n___ send_choice_location ___")

    user_id, chat_id, message_id, player_session = (get_kwargs(
        ("user_id", "chat_id", "message_id", "player_session"), kwargs))

    non_finished_progresses = UserPointProgressRepository.filter(player_session=player_session, is_finished=False)
    if not non_finished_progresses:
        bot.edit_message_text("Поздравляем, вы прошли все испытания!", chat_id, message_id,
                              reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text=" 🎉 ",
                                                                                           callback_data="finish")))
    else:
        bot.edit_message_text("Выберите локацию:", chat_id, message_id,
                              reply_markup=objects_keyboard(objects=non_finished_progresses,
                                                            callback_data="select_point:"))


@bot.callback_query_handler(func=lambda c: c.data.startswith("select_point:"))
@with_context(include_player_session=True)
@log_exceptions()
def call_select_point(**kwargs):
    logging.info("\n\n___ call_select_point ___")

    data, message_id, chat_id, player, player_session = (get_kwargs(
        ("data", "message_id", "chat_id", "player", "player_session"), kwargs))
    point_id = int(data.split(":")[1])

    point = PointRepository.get(point_id=point_id)

    logging.info(f"{player}: отправляется на точку {point}")

    PlayerSessionRepository.update_instance(player_session, current_point=point)

    logging.debug(f"{player_session}: {player_session.current_point}")

    bot.edit_message_text(f'Пункт назначения - {point.title}! \n'
                          f'Вот <a href="{point.location}">локация</a>.', chat_id, message_id,
                          parse_mode='HTML', disable_web_page_preview=True)

    bot.send_message(chat_id, "Когда прибудете на место, нажмите:",
                     reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="Я на месте 🎉",
                                                                                  callback_data="arrived")))

    logging.debug(f"{player}: Отправлена локация и кнопка <я на месте>")


@bot.callback_query_handler(func=lambda callback: callback.data == "arrived")
@with_context(include_user_point_progress=True)
@log_exceptions()
def call_arrived(**kwargs):
    logging.info("\n\n___ call_arrived ___")

    message_id, chat_id, player, player_session, current_point, user_point_progress, clues_left = (get_kwargs(
        ("message_id", "chat_id", "player", "player_session", "current_point",
         "user_point_progress", "clues_left"), kwargs))
    task = current_point.task
    bot.delete_message(chat_id, message_id)

    logging.info(f"{player}: прибыл на точку {current_point}")

    try:
        UserPointProgressRepository.update_instance(
            user_point_progress,
            started_at=datetime.now(UTC))
    except ValueError as error:
        logging.error(f"Ошибка обновления UserPointProgress: {error}")
    else:
        logging.debug("UserPointProgress успешно обновлен.")

    with open(task["photo"], 'rb') as photo:
        bot.send_photo(
            chat_id,
            photo,
            caption=f"<b>📍 {current_point.title}</b>",
            parse_mode="HTML")

    bot.send_message(chat_id, task["value"])

    if "voice" in task:
        file_path = task["voice"]
        with open(file_path, 'rb') as voice:
            bot.send_voice(chat_id=chat_id, voice=voice)

    logging.debug(f"{player}: Отправлено задание точки {current_point}.")

    safe_set_state(player.user_id, GameState.waiting_for_answer, chat_id)


@bot.callback_query_handler(func=lambda call: call.data == "finish")
@with_context(include_player_session=True)
@log_exceptions()
def call_finish(**kwargs):
    logging.info(f"\n\n___ call_finish ___")

    message_id, player, chat_id, player_session = (
        get_kwargs(("message_id", "player", "chat_id", "player_session"), kwargs))
    finish_data = player_session.game_session.game_info.finish
    logging.info(f"{player}: вышел в финал.")

    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)

    bot.send_message(chat_id,
                     f"{finish_data['value']}\n\n📍 <a href=\"{finish_data['location']}\">Открыть локацию</a>",
                     parse_mode="HTML", disable_web_page_preview=True)

    PlayerSessionRepository.update_instance(player_session, status="finished")
    logging.debug(f"{player}:Информация о финальной точке успешно отправлена.")
