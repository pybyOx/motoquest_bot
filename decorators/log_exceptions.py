from __future__ import annotations
from functools import wraps
import logging
from core.container import get_container
from config_data.config import MAIN_ADMIN_ID
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from core.dto.context import Context
    from database.models.user import User

container = get_container()
user_states_service = container.user_states_service
user_repo = container.user_repo
ui_service = container.ui_service


def log_exceptions():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ctx: Context = kwargs["ctx"]
            user: User = ctx.user
            user_id: int = ctx.user_id
            try:
                return func(*args, **kwargs)
            except Exception:
                logging.error(f"[{user_id}]: Исключение в {func.__name__}", exc_info=True)

                attempts = user.recovery_attempts or 0

                if attempts < 2:
                    logging.info(f"[{user_id}] auto-recovery attempt")

                    try:
                        user_repo.increment_recovery_attempts(user_id=user_id)

                        user_states_service.recover(
                            user_id=user_id,
                            notify_text="Произошла ошибка. Попробуйте ещё раз."
                        )

                        user_repo.reset_recovery_attempts(user_id=user_id)

                        return

                    except Exception:
                        logging.error(f"[{user_id}] auto-recovery failed", exc_info=True)

                logging.critical(f"[{user_id}] recovery failed окончательно. Требуется ручной recovery.")

                ui_service.send_msg(
                    chat_id=MAIN_ADMIN_ID,
                    text=f"{user_id}: требуется ручной recovery"
                )
                ui_service.show_user_ui(
                    user=user,
                    text="Произошла ошибка. Ожидайте, пока администратор восстановит игру."
                )
                user_repo.set_error(user_id)

                return
        return wrapper
    return decorator
