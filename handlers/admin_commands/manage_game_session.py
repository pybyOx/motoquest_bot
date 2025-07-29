from loader import bot
from config_data.config import ADMIN_IDS
from database.database_model import GameSession, UserPointProgress
from repositories.repositories import (GameSessionRepository, PlayerSessionRepository, UserPointProgressRepository,
                                       PlayerRepository)
from utils.decorators.with_context import with_context
from utils.decorators.ask_confirmation import ask_confirmation
from keyboards.inline.keyboards import (start_or_delete_keyboard, objects_keyboard, combine_keyboards,
                                        cancel_or_back_keyboard)
from utils.choice_location import send_choice_location
from utils.misc.get_kwargs import get_kwargs
from peewee import DoesNotExist
from utils.misc.exceptions import CreationError, AlreadyExistsError, DeletionError
import logging
from handlers.admin_commands.support_utils import user_steps, reset_user_session, bot_messages


@bot.message_handler(commands=["manage_game"])
@with_context()
def manage_game_handler(**kwargs):
    logging.info(f"\n\n___manage_game_handler___")
    user_id, chat_id = get_kwargs(["user_id", "chat_id"], kwargs)

    if user_id not in ADMIN_IDS:
        bot.send_message(chat_id, "⛔ Только для администраторов.")
        return

    reset_user_session(user_id, chat_id)

    show_sessions_selection(user_id, chat_id)


def show_sessions_selection(user_id, chat_id):
    logging.info(f"\n\n___ show_sessions_selection ___")

    user_steps[user_id].append((show_sessions_selection, (user_id, chat_id), {}))
    logging.debug(f"Добавили в user_steps: {user_steps[user_id]}")

    game_sessions = GameSessionRepository.filter(finished=False)
    if not game_sessions:
        bot.send_message(chat_id, "Нет активных игровых сессий.")
        return

    msg = bot.send_message(chat_id, f"Выберите игровую сессию, которой хотите управлять:",
                           reply_markup=combine_keyboards(
                               objects_keyboard(game_sessions, "manage_game:"),
                               cancel_or_back_keyboard(False)))
    logging.debug(f"Отправили выбор игры")

    bot_messages[user_id].append(msg.message_id)
    logging.debug(f"Добавили в bot_messages: {bot_messages[user_id]}")


@bot.callback_query_handler(func=lambda c: c.data.startswith("manage_game:"))
@with_context()
def manage_game_by_id(**kwargs):
    logging.info(f"\n\n___manage_game_by_id___")
    call, user_id, chat_id = get_kwargs(["message_or_callback", "user_id", "chat_id"], kwargs)
    session_id = int(call.data.split(":")[1])

    try:
        game_session = GameSessionRepository.get(session_id=session_id)
    except (DoesNotExist, Exception) as error:
        bot.edit_message_text(f"Не найдена игра (id {session_id})", chat_id, call.message.message_id, reply_markup=None)
        logging.error(f"При получении GameSession: {error}", exc_info=True)
        return

    bot.edit_message_text(text=f"Игра: {game_session}",
                          chat_id=chat_id, message_id=bot_messages[user_id][-1], reply_markup=None)
    logging.debug(f"Заменили вопрос с выбором игры на ответ.")

    show_action_step(user_id, chat_id, session_id)


def show_action_step(user_id, chat_id, session_id):
    logging.info(f"\n\n___ show_action_step ___")

    user_steps[user_id].append((show_action_step, (user_id, chat_id, session_id), {}))
    logging.debug(f"Добавили в user_steps: {user_steps[user_id]}")

    msg = bot.send_message(chat_id, f"Выберите действие:", reply_markup=combine_keyboards(
        start_or_delete_keyboard(session_id), cancel_or_back_keyboard()))
    logging.debug(f"Отправлен выбор старт или удаление.")

    bot_messages[user_id].append(msg.message_id)
    logging.debug(f"Добавили в bot_messages: {bot_messages[user_id]}")


@bot.callback_query_handler(func=lambda c: c.data.startswith(("delete_game:", "start_game:")))
@with_context()
def call_manager(**kwargs):
    logging.info(f"\n\n___call_manager___")

    call, user_id, chat_id = get_kwargs(["message_or_callback", "user_id", "chat_id"], kwargs)
    callback_data = call.data
    session_id = int(call.data.split(":")[1])
    try:
        game_session = GameSessionRepository.get(session_id=session_id)
    except (DoesNotExist, Exception) as error:
        bot.edit_message_text(f"Не найдена игра (id {session_id})", chat_id, call.message.message_id, reply_markup=None)
        logging.error(f"При получении GameSession: {error}", exc_info=True)
        return

    # === УДАЛЕНИЕ ИГРЫ ===
    if callback_data.startswith("delete_game:"):
        logging.debug(f"Удаление {game_session}")
        msg = bot.edit_message_text(f"Удаление {game_session}", chat_id=chat_id, message_id=call.message.message_id,
                                    reply_markup=None)
        bot_messages[user_id].append(msg.message_id)
        delete_game_session(game_session, user_id=user_id)

    # === СТАРТ ИГРЫ ===
    if callback_data.startswith("start_game:"):
        logging.debug(f"Старт {game_session}")
        msg = bot.edit_message_text(f"Старт {game_session}", chat_id=chat_id, message_id=call.message.message_id,
                                    reply_markup=None)
        bot_messages[user_id].append(msg.message_id)
        start_game_session(game_session, user_id=user_id)


@ask_confirmation("Вы уверены, что хотите удалить эту игру?")
def delete_game_session(game_session: GameSession, user_id: int):
    logging.info(f"\n\n___delete_game_session___")

    related_sessions = PlayerSessionRepository.filter(game_session=game_session)
    if related_sessions:
        for player_session in related_sessions:
            if player_session.status == "registered":
                bot.send_message(player_session.player.user_id,
                                 f"⚠️ Игра {player_session.game_session}, на которую вы были записаны, отменена.")
        logging.debug(f"Отправлены сообщения об отмене игры пользователям, зарегистрировавшимся на {game_session}")
    try:
        GameSessionRepository.delete_instance(game_session)
    except DeletionError as error:
        bot.send_message(user_id, f"Ошибка удаления {game_session}.")
        logging.error(f"При удалении GameSession: {error}", exc_info=True)
    else:
        bot.edit_message_text(f"✅ Игра '{game_session}' успешно удалена.", user_id, bot_messages[user_id][-1])
        logging.debug(f"✅ Игра '{game_session}' успешно удалена.")


@ask_confirmation("Вы уверены, что хотите начать эту игру?")
def start_game_session(game_session: GameSession, user_id: int):
    logging.info(f"\n\n___start_game_session___")

    for player_session in game_session.player_sessions:
        creation_failed = False  # флаг для ошибки

        for point in game_session.game_info.points:

            try:

                UserPointProgressRepository.create(player_session=player_session, point=point)

            except AlreadyExistsError:

                logging.error(f"UserPointProgress уже существует. Пробуем пересоздать."
                              f"\n player_session: ({player_session.player_session_id})"
                              f"\n point: ({point}) ", exc_info=True)

                try:
                    UserPointProgressRepository.delete((UserPointProgress.player_session == player_session) &
                                                       (UserPointProgress.point == point))
                    UserPointProgressRepository.create(player_session=player_session, point=point)
                except Exception as e:
                    logging.error(f"Не удалось пересоздать UserPointProgress: {e}", exc_info=True)
                    creation_failed = True
                    break
                else:
                    logging.debug("UserPointProgress пересоздан.")

            except CreationError as e:

                logging.error(f"Ошибка создания UserPointProgress."
                              f"\n player_session: ({player_session.player_session_id})"
                              f"\n point: ({point}) "
                              f"\n error: {e}", exc_info=True)
                try:
                    UserPointProgressRepository.delete(UserPointProgress.player_session == player_session)
                except (DoesNotExist, DeletionError) as error:
                    logging.error(f"При удалении UserPointProgress: {error}", exc_info=True)

                creation_failed = True
                break

        if creation_failed:
            bot.send_message(user_id, f"Не удалось создать прогресс по точкам для {player_session}")
            logging.debug(f"Не удалось создать прогресс по точкам для {player_session}")
            continue

        player = player_session.player

        PlayerSessionRepository.update_instance(player_session, status="started")
        logging.debug(f"{player}:Поменяли статус для {player_session} на started")

        PlayerRepository.update_instance(player, current_player_session=player_session)
        logging.debug(f"{player}: current_player_session - {player_session} ")

        bot.send_message(player.user_id, "🏁 Игра началась!")
        logging.debug(f"{player}: отправили сообщение о начале игры")

        send_choice_location(player_session=player_session)
        logging.debug(f"{player}: выбор локации")

    bot.edit_message_text(f"✅ Игра '{game_session}' успешно стартовала.", user_id, bot_messages[user_id][-1])
