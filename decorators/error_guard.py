from __future__ import annotations
from functools import wraps
from core.container import get_container
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.dto.context import Context

container = get_container()
bot = container.bot
ui_service = container.ui_service


def error_guard():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ctx: Context = kwargs["ctx"]

            if ctx.user.is_error:

                if ctx.content_type == "callback":
                    callback_id: int | None = ctx.callback_id
                    if callback_id:
                        bot.answer_callback_query(
                            callback_query_id=callback_id,
                            text="Ошибка"
                        )

                ui_service.send_msg(
                    chat_id=ctx.chat_id,
                    text="Произошла ошибка. Ожидайте, пока администратор восстановит игру."
                )
                return

            return func(*args, **kwargs)
        return wrapper
    return decorator
