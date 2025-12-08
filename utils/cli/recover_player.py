from loader import bot
from utils.cli.supporting_func.check_data import get_data_from_argv
from utils.misc.exceptions import CliInputError
import logging
from repositories.repositories import PlayerRepository
from handlers.admin_commands.manage_game_session import manage_game_handler
from handlers.custom_handlers.states_handlers import (call_get_clue, call_review, handle_user_answer,
                                                      handle_waiting_for_review)
from handlers.default_commands.start import bot_start
from handlers.users_commands.cancel import call_cancel, send_player_sessions_keyboard
from handlers.users_commands.help import bot_help
from handlers.users_commands.info import send_info
from handlers.users_commands.register import call_register, send_sessions_keyboard
from utils.choice_location import call_arrived, call_finish, call_select_point, send_choice_location
from utils.decorators.ask_confirmation import handle_confirmation_callback

recovery_map = {
    "manage_game_handler": manage_game_handler,
    "call_get_clue": call_get_clue,
    "call_review": call_review,
    "handle_user_answer": handle_user_answer,
    "handle_waiting_for_review": handle_waiting_for_review,
    "bot_start": bot_start,
    "call_cancel": call_cancel,
    "send_player_sessions_keyboard": send_player_sessions_keyboard,
    "bot_help": bot_help,
    "send_info": send_info,
    "call_register": call_register,
    "send_sessions_keyboard": send_sessions_keyboard,
    "call_arrived": call_arrived,
    "call_finish": call_finish,
    "call_select_point": call_select_point,
    "send_choice_location": send_choice_location,
    "handle_confirmation_callback": handle_confirmation_callback}


def recover_players(player_id: int):

    player = PlayerRepository.get(user_id=player_id)
    func_data = player.current_func
    if not func_data:
        raise ValueError(f"Не нашли текущую функцию для {player}")
    PlayerRepository.update_instance(player, current_func=None)
    bot.delete_state(player_id)
    func_name = next(iter(func_data))
    func_obj = recovery_map.get(func_name)
    if not func_obj:
        raise ValueError(f"Функция {func_name} не найдена в recovery_map")
    args, kwargs = func_data[func_name]

    func_obj(*args, **kwargs)


if __name__ == "__main__":
    """
    После изменений кода сначала вкл-выкл бот, потом
    python -m utils.cli.recover_player {user_id}
    """

    try:
        user_id = int(get_data_from_argv(length=1, index=0))
        recover_players(user_id)
    except (CliInputError, Exception) as error:
        logging.error(f"{error}", exc_info=True)
