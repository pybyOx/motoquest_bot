from peewee import DoesNotExist
from loader import bot
from utils.decorators.with_context import with_context
from utils.decorators.ask_confirmation import ask_confirmation
from utils.misc.get_kwargs import get_kwargs
from config_data.config import ADMIN_IDS
from states.states_game import CreateGameStates
from datetime import datetime
from repositories.repositories import GameInfoRepository, GameSessionRepository
from utils.misc.exceptions import AlreadyExistsError, CreationError
import logging
from keyboards.inline_keyboards import cancel_or_back_keyboard, city_keyboard, combine_keyboards, objects_keyboard
from utils.cli.supporting_func.check_data import is_map_link
from handlers.admin_commands.support_utils import reset_user_session, user_steps, bot_messages, game_data


@bot.message_handler(commands=["create_game"])
@with_context()
def create_game_handler(**kwargs):
    logging.info(f"\n\n___create_game_handler___")
    message, user_id, chat_id = get_kwargs(["message_or_callback", "user_id", "chat_id"], kwargs)

    if user_id not in ADMIN_IDS:
        bot.send_message(chat_id, "⛔ Только для администраторов.")
        return

    reset_user_session(user_id, chat_id)

    show_game_selection(user_id, chat_id)


def show_game_selection(user_id, chat_id):
    logging.info(f"\n\n___show_game_selection___")

    user_steps[user_id].append((show_game_selection, (user_id, chat_id), {}))
    logging.debug(f"Добавили в user_steps: {user_steps[user_id]}")

    try:
        games = GameInfoRepository.get_all()
    except DoesNotExist:
        bot.send_message(chat_id, "Объектов GameInfo не найдено")
    else:

        msg = bot.send_message(chat_id, "Выберите игру:", reply_markup=combine_keyboards(
            objects_keyboard(games, "create_game:"), cancel_or_back_keyboard(False)))
        logging.debug(f"Отправили выбор игры")

        bot_messages[user_id].append(msg.message_id)
        logging.debug(f"Добавили в bot_messages: {bot_messages[user_id]}")


@bot.callback_query_handler(func=lambda c: c.data.startswith("create_game:"))
@with_context()
def handle_game(**kwargs):
    logging.info(f"\n\n___handle_game___")

    call, user_id, chat_id = get_kwargs(["message_or_callback", "user_id", "chat_id"], kwargs)

    try:
        game_info = GameInfoRepository.get(game_id=int(call.data.split(":")[1]))

    except (DoesNotExist, Exception) as error:
        bot.send_message(chat_id, "Ошибка получения игры по этому id.")
        logging.error(f"При получении GameInfo: {error}", exc_info=True)

    else:
        game_data[user_id]["game_info"] = game_info
        logging.debug(f"Обновили game_data: {game_data[user_id]}")

        bot.edit_message_text(text=f"Игра: {game_info.title}", chat_id=chat_id,
                              message_id=bot_messages[user_id][-1], reply_markup=None)
        logging.debug(f"Заменили вопрос с выбором игры на ответ.")

        show_city_step(user_id, chat_id)


def show_city_step(user_id, chat_id):
    logging.info(f"\n\n___ show_city_step ___")

    user_steps[user_id].append((show_city_step, (user_id, chat_id), {}))
    logging.debug(f"Добавили в user_steps: {user_steps[user_id]}")

    msg = bot.send_message(chat_id, "Выберите город проведения:",
                           reply_markup=combine_keyboards(city_keyboard(), cancel_or_back_keyboard()))
    logging.debug(f"Отправили выбор города")

    bot_messages[user_id].append(msg.message_id)
    logging.debug(f"Добавили в bot_messages: {bot_messages[user_id]}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("city:"))
@with_context()
def handle_city(**kwargs):
    logging.info(f"\n\n___handle_city___")

    call, user_id, chat_id = get_kwargs(["message_or_callback", "user_id", "chat_id"], kwargs)

    city_map = {"nha_trang": "Нячанг", "hanoi": "Ханой"}
    city = city_map.get(call.data.split(":")[1], "Неизвестно")
    game_data[user_id]["city"] = city
    logging.debug(f"Обновили game_data: {game_data[user_id]}")

    bot.edit_message_text(text=f"Город: {city}", chat_id=chat_id,
                          message_id=bot_messages[user_id][-1], reply_markup=None)
    logging.debug(f"Заменили вопрос с выбором города на ответ.")

    ask_location(user_id, chat_id)


def ask_location(user_id, chat_id):
    logging.info(f"\n\n___ask_location___")

    user_steps[user_id].append((ask_location, (user_id, chat_id), {}))
    logging.debug(f"Добавили в user_steps: {user_steps[user_id]}")

    msg = bot.send_message(chat_id, "Введите место встречи:", reply_markup=cancel_or_back_keyboard())
    logging.debug(f"Отправили выбор места встречи")

    bot_messages[user_id].append(msg.message_id)
    logging.debug(f"Добавили в bot_messages: {bot_messages[user_id]}")

    bot.set_state(user_id, CreateGameStates.waiting_for_location)
    logging.debug("Состояние waiting_for_location")


@bot.message_handler(state=CreateGameStates.waiting_for_location)
@with_context()
def receive_location(**kwargs):
    logging.info(f"\n\n___receive_location___")

    message, user_id, chat_id = get_kwargs(["message_or_callback", "user_id", "chat_id"], kwargs)

    if not is_map_link(message.text.strip()):
        try:
            bot.delete_message(chat_id, message.message_id)
        except Exception:
            pass
        message = bot.send_message(chat_id, "Некорректная ссылка, попробуйте еще раз.")
        bot.delete_message(chat_id, message.message_id)
        return

    game_data[user_id]["location"] = f"📍 [Открыть локацию на карте]({message.text.strip()})"
    logging.debug(f"Обновили game_data: {game_data[user_id]}")

    bot.edit_message_reply_markup(chat_id, bot_messages[user_id][-1], reply_markup=None)
    logging.debug(f"В вопросе с выбором города удалили клавиатуру.")

    ask_date(user_id, chat_id)


def ask_date(user_id, chat_id):
    logging.info(f"\n\n___ask_date___")

    user_steps[user_id].append((ask_date, (user_id, chat_id), {}))
    logging.debug(f"Добавили в user_steps: {user_steps[user_id]}")

    msg = bot.send_message(chat_id, "Введите дату и время начала (в формате ДД.ММ.ГГГГ ЧЧ:ММ):",
                           reply_markup=cancel_or_back_keyboard())
    logging.debug(f"Отправили выбор даты")

    bot_messages[user_id].append(msg.message_id)
    logging.debug(f"Добавили в bot_messages: {bot_messages[user_id]}")

    bot.set_state(user_id, CreateGameStates.waiting_for_date)
    logging.debug("Состояние waiting_for_date")


@bot.message_handler(state=CreateGameStates.waiting_for_date)
@with_context()
def receive_date(**kwargs):
    logging.info(f"\n\n___receive_date___")

    message, user_id, chat_id = get_kwargs(["message_or_callback", "user_id", "chat_id"], kwargs)

    try:
        date = datetime.strptime(message.text.strip(), "%d.%m.%Y %H:%M")
    except ValueError:
        message = bot.send_message(chat_id, "Неверный формат. Попробуй ещё раз: ДД.ММ.ГГГГ ЧЧ:ММ")
        bot.delete_message(chat_id, message.message_id)
        return

    bot.edit_message_reply_markup(chat_id, bot_messages[user_id][-1], reply_markup=None)
    logging.debug(f"В вопросе с выбором даты удалили клавиатуру.")

    create_game_session(user_id=user_id, chat_id=chat_id,
                        game_info=game_data[user_id]["game_info"],
                        city=game_data[user_id]["city"],
                        location=game_data[user_id]["location"],
                        date=date)


@ask_confirmation("Все верно?")
def create_game_session(user_id, chat_id, game_info, city, location, date):
    logging.info(f"\n\n___create_game_session___")
    try:
        session = GameSessionRepository.create(game_info=game_info, city=city, location=location, date=date)
    except AlreadyExistsError:
        bot.send_message(chat_id, "GameSession с такими данными уже существует.")
    except CreationError as error:
        bot.send_message(chat_id, "Ошибка создания GameSession.")
        logging.error(f"[При создании GameSession: {error}", exc_info=True)
    else:
        bot.send_message(chat_id, f"✅ Игра создана:\n{session}")
    finally:
        reset_user_session(user_id, chat_id)
