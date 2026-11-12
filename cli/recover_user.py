from core.exceptions import CliInputError
import logging
from core.utils.check_data import get_data_from_argv
from core.container import get_container
from database.lifecycle import setup_db


def recover_user(tg_id: int) -> None:
    try:
        get_container().user_states_service.recover(user_id=tg_id)
    except (CliInputError, Exception) as error:
        logging.error(f"{error}", exc_info=True)


def main() -> None:
    """Точка входа команды: python -m cli.recover_user <telegram id>

    После изменений кода сначала перезапустить бота.
    """
    setup_db()
    user_id = int(get_data_from_argv(length=1, index=1))
    recover_user(user_id)


if __name__ == "__main__":
    main()
