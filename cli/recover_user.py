from core.exceptions import CliInputError
import logging
from core.utils.check_data import get_data_from_argv
from core.container import get_container

container = get_container()
user_states_service = container.user_states_service


def recover_user(tg_id: int) -> None:
    try:
        user_states_service.recover(user_id=tg_id)
    except (CliInputError, Exception) as error:
        logging.error(f"{error}", exc_info=True)


if __name__ == "__main__":
    """
    После изменений кода сначала вкл-выкл бот, потом
    python -m cli.recover_user 395578226
    """
    user_id = int(get_data_from_argv(length=1, index=1))
    recover_user(user_id)
