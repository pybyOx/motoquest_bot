from loader import bot
from utils.cli.supporting_func.check_data import get_data_from_argv
from utils.misc.exceptions import CliInputError
import logging
from repositories.repositories import PlayerRepository
from utils.choice_location import call_select_point

recovery_map = {
    "call_select_point": call_select_point}


def recover_players(player_id: int):

    player = PlayerRepository.get(user_id=player_id)
    func_data = player.current_func
    if not func_data:
        raise ValueError(f"Не нашли текущую функцию для {player}")
    PlayerRepository.update_instance(player, current_func=None)
    bot.delete_state(player_id)
    func_name = next(iter(func_data))
    func_obj = recovery_map.get(func_name)
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
