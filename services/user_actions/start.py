import logging
from bot.loader import bot
from config_data.config import ADMIN_IDS
from keyboards.inline_keyboards import start_keyboard
from repositories.repositories import PlayerRepository, PlayerSessionRepository
from utils.decorators.log_exceptions import log_exceptions
from utils.decorators.with_context import with_context
from utils.misc.exceptions import AlreadyExistsError
from utils.misc.get_kwargs import get_kwargs
from utils.set_bot_commands import set_commands
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.database_model import Player


@with_context()
@log_exceptions()
def start_command(**kwargs):
    user_id, username, chat_id = get_kwargs(("user_id", "username", "chat_id"), kwargs)

    set_commands(user_id)

    player, is_new = get_or_create_player(user_id, username)

    greet_user(chat_id, username, is_new)

    if user_id in ADMIN_IDS:
        return

    if has_active_game(player):
        bot.send_message(
            chat_id,
            "Вы уже участвуете в игре. Чтобы продолжить, выполняйте задания."
        )
        return

    bot.send_message(
        chat_id,
        "Доступные команды:",
        reply_markup=start_keyboard()
    )


def get_or_create_player(user_id: int, username: str) -> tuple["Player", bool]:
    try:
        player = PlayerRepository.create(
            user_id=user_id,
            username=username
        )
    except AlreadyExistsError:
        return PlayerRepository.get(user_id=user_id), False
    else:
        logging.info(f"{player}: зарегистрирован.")
        return player, True


def greet_user(chat_id: int, username: str, is_new: bool):
    if is_new:
        bot.send_message(chat_id, f"Привет, {username}!")
    else:
        bot.send_message(chat_id, f"Рад тебя снова видеть, {username}!")


def has_active_game(player: "Player") -> bool:
    return PlayerSessionRepository.filter(
        player=player,
        status="started"
    ).exists()
