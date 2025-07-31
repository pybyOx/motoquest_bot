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


@bot.message_handler(commands=["start"])
@log_exceptions()
@with_context()
def bot_start(**kwargs):

    user_id, username, chat_id = get_kwargs(["user_id", "username", "chat_id"], kwargs)

    set_commands(user_id)
    try:
        player = PlayerRepository.create(user_id=user_id, username=username)
        bot.send_message(chat_id, f"Привет, {username}!")
        logging.info(f"{player}: зарегистрирован.")
    except AlreadyExistsError:
        bot.send_message(chat_id, f"Рад тебя снова видеть, {username}!")
    except CreationError as error:
        logging.error(f"[При создании Player: {error}", exc_info=True)
        raise

    if user_id not in ADMIN_IDS:

        if PlayerSessionRepository.filter(player_id=user_id, status="started"):
            bot.send_message(chat_id, "Вы уже участвуете в игре. Чтобы продолжить, выполняйте задания.")
            return

        bot.send_message(chat_id, "\tДоступные команды:\n", reply_markup=start_keyboard())


@bot.callback_query_handler(func=lambda call: call.data == "info")
@log_exceptions()
@with_context()
def call_command_info(**kwargs):
    logging.info("\n\n___ call_command_info ___")

    call, user_id, chat_id = get_kwargs(["message_or_callback", "user_id", "chat_id"], kwargs)
    bot.delete_message(chat_id, call.message.message_id)

    send_info(call)


@bot.callback_query_handler(func=lambda call: call.data == "help")
@log_exceptions()
@with_context()
def call_command_help(**kwargs):
    logging.info("\n\n___ call_command_help ___")

    call, chat_id = get_kwargs(["message_or_callback", "chat_id"], kwargs)
    bot.delete_message(chat_id, call.message.message_id)

    bot.send_message(chat_id, "🆘 *Нужна помощь?*\n\n"
                              "📨 Напишите в поддержку: @tgoxx\n",
                     parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data == "register")
@log_exceptions()
@with_context()
def call_command_register(**kwargs):
    logging.info("\n\n___ call_command_register ___")

    call, chat_id = get_kwargs(["message_or_callback", "chat_id"], kwargs)
    bot.delete_message(chat_id, call.message.message_id)

    send_sessions_keyboard(call)


@bot.callback_query_handler(func=lambda call: call.data == "cancel")
@log_exceptions()
@with_context()
def call_command_cancel(**kwargs):
    logging.info("\n\n___ call_command_cancel ___")

    call, user_id, chat_id = get_kwargs(["message_or_callback", "user_id", "chat_id"], kwargs)
    bot.delete_message(chat_id, call.message.message_id)

    send_player_sessions_keyboard(call)
