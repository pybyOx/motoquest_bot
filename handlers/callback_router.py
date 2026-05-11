from core.container import get_container
from decorators.log_exceptions import log_exceptions
from decorators.error_guard import error_guard
from decorators.with_context import with_context
from core.utils.parse_callback import parse_callback_data
import logging
from typing import TYPE_CHECKING

bot = get_container().bot

if TYPE_CHECKING:
    from core.dto.context import Context
    from states.base_state import BaseUserState


@bot.callback_query_handler(func=lambda c: True)
@with_context()
@error_guard()
@log_exceptions()
def callback_router(**kwargs):
    ctx: Context = kwargs["ctx"]

    callback_type, payload = parse_callback_data(ctx.data)

    state_obj: BaseUserState = ctx.state_obj

    if not state_obj.can_handle(callback_type):
        logging.warning(f"Unexpected callback {callback_type} for state {ctx.user_state}")
        return

    extra_kwargs = {"payload": payload} if payload is not None else {}

    state_obj.handle_callback(callback_type=callback_type, **kwargs,  **extra_kwargs)
