from loader import bot
from utils.decorators.with_context import with_context
from utils.decorators.log_exceptions import log_exceptions
from utils.misc.get_kwargs import get_kwargs
from functools import wraps
from keyboards.inline_keyboards import confirm_keyboard


# Хранилище ожидающих подтверждений: user_id -> callback
user_confirmations = {}


def ask_confirmation(question="Вы уверены?"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = get_kwargs(['user_id'], kwargs)[0]

            user_confirmations[user_id] = (func, args, kwargs)

            bot.send_message(user_id, question, reply_markup=confirm_keyboard())
        return wrapper
    return decorator


@bot.callback_query_handler(func=lambda c: c.data in ["confirm_yes", "confirm_no"])
@log_exceptions()
@with_context()
def handle_confirmation_callback(**kwargs):
    message_id, user_id, chat_id, data = get_kwargs(["message_id", "user_id", "chat_id", "data"], kwargs)

    if user_id not in user_confirmations:
        bot.edit_message_text("Нет ожидающего действия.", chat_id, message_id, reply_markup=None)
        return

    bot.delete_message(chat_id, message_id)

    if data == "confirm_yes":
        func, args, kwargs = user_confirmations.pop(user_id)

        func(*args, **kwargs)
    else:
        user_confirmations.pop(user_id)
        bot.send_message(chat_id, "❌ Действие отменено.")
