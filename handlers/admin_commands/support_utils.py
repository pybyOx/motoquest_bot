from loader import bot
from utils.decorators.with_context import with_context
from utils.misc.get_kwargs import get_kwargs
import logging


game_data = {}  # для хранения информации об игре
bot_messages = {}  # для хранения сообщений от бота
user_steps = {}  # стек функций


@bot.callback_query_handler(func=lambda call: call.data in ["cancel_action", "back"])
@with_context()
def handle_cancel_or_back(**kwargs):
    logging.info(f"\n\n___handle_cancel_or_back___")
    call, user_id, chat_id = get_kwargs(["message_or_callback", "user_id", "chat_id"], kwargs)

    if call.data == "cancel_action":
        logging.debug("Отмена действия")

        bot.edit_message_text("🚫 Действие отменено.", chat_id, bot_messages[user_id][-1], reply_markup=None)
        logging.debug(f"Заменили последний вопрос на Действие отменено.")

        reset_user_session(user_id, chat_id)

    elif call.data == "back":
        logging.debug("Шаг назад")

        for _ in range(2):
            message_id = bot_messages[user_id].pop()
            bot.delete_message(chat_id, message_id)
        logging.debug(f"Удалили два последних сообщения из bot_messages: {bot_messages[user_id]}")

        if len(user_steps[user_id]) > 1:
            user_steps[user_id].pop()
            logging.debug(f"Удалили из user_steps последнюю функцию: {user_steps[user_id]}")

            func, args, kwargs = user_steps[user_id][-1]
            func(*args, **kwargs)
        else:
            bot.answer_callback_query(call.id, text="⬅️ Назад невозможно", show_alert=False)


def reset_user_session(user_id, chat_id):
    logging.info(f"\n\n___reset_user_session___")
    bot.delete_state(user_id, chat_id)
    game_data[user_id] = {}
    bot_messages[user_id] = []
    user_steps[user_id] = []
    logging.debug(f"Очистили состояние пользователя:\n"
                  f"state: {bot.get_state(user_id, chat_id)}\n"
                  f"game_data[user_id]: {game_data[user_id]}\n"
                  f"bot_messages[user_id]: {bot_messages[user_id]}\n"
                  f"user_steps[user_id]: {user_steps[user_id]}")
