from telebot.types import BotCommand, BotCommandScopeChat
from config_data.config import PLAYER_COMMANDS, ADMIN_COMMANDS, ADMIN_IDS
from loader import bot


def set_commands(user_id) -> None:
    """Задает разные команды для пользователя, в зависимости от того, является он админом или нет.
    :param user_id: ID пользователя."""

    if user_id in ADMIN_IDS:
        bot.set_my_commands(
            [BotCommand(*i) for i in ADMIN_COMMANDS],
            scope=BotCommandScopeChat(chat_id=user_id)
        )
    else:
        bot.set_my_commands(
            [BotCommand(*i) for i in PLAYER_COMMANDS],
            scope=BotCommandScopeChat(chat_id=user_id)
        )
