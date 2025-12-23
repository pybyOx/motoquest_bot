from loader import bot
from utils.misc.exceptions import CreationError, AlreadyExistsError
import logging
from utils.decorators.with_context import with_context
from utils.decorators.log_exceptions import log_exceptions
from utils.set_bot_commands import set_commands
from keyboards.inline_keyboards import start_keyboard
from config_data.config import ADMIN_IDS
from utils.misc.get_kwargs import get_kwargs
from repositories.repositories import PlayerSessionRepository, PlayerRepository
from handlers.users_commands.register import send_sessions_keyboard
from handlers.users_commands.cancel import send_player_sessions_keyboard
from handlers.users_commands.info import send_info
from telebot.types import CallbackQuery


@bot.message_handler(commands=["start"])
@with_context()
@log_exceptions()
def bot_start(**kwargs):

    user_id, username, chat_id = get_kwargs(("user_id", "username", "chat_id"), kwargs)

    set_commands(user_id)
    try:
        player = PlayerRepository.create(user_id=user_id, username=username)
    except AlreadyExistsError:
        bot.send_message(chat_id, f"Рад тебя снова видеть, {username}!")
    else:
        bot.send_message(chat_id, f"Привет, {username}!")
        logging.info(f"{player}: зарегистрирован.")

    if user_id not in ADMIN_IDS:

        if PlayerSessionRepository.filter(player_id=user_id, status="started"):
            bot.send_message(chat_id, "Вы уже участвуете в игре. Чтобы продолжить, выполняйте задания.")
            return

        bot.send_message(chat_id, "\tДоступные команды:\n", reply_markup=start_keyboard())


@bot.callback_query_handler(func=lambda call: call.data == "info")
def call_command_info(callback: CallbackQuery):
    send_info(callback)


@bot.callback_query_handler(func=lambda call: call.data == "help")
def call_command_help(callback: CallbackQuery):

    bot.send_message(callback.message.chat.id, "🆘 *Нужна помощь?*\n\n"
                                               "📨 Напишите в поддержку: @tgoxx\n",
                     parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data == "register")
def call_command_register(callback: CallbackQuery):
    send_sessions_keyboard(callback)


@bot.callback_query_handler(func=lambda call: call.data == "cancel")
def call_command_cancel(callback: CallbackQuery):
    send_player_sessions_keyboard(callback)
