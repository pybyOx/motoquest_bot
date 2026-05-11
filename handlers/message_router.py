from decorators.with_context import with_context
from core.container import get_container
from decorators.log_exceptions import log_exceptions
from decorators.error_guard import error_guard
from typing import TYPE_CHECKING

bot = get_container().bot

if TYPE_CHECKING:
    from core.dto.context import Context
    from states.base_state import BaseUserState


@bot.message_handler(content_types=["text", "photo", "document"])
@with_context()
@error_guard()
@log_exceptions()
def message_router(**kwargs):
    ctx: Context = kwargs["ctx"]
    state_obj: BaseUserState = ctx.state_obj
    command = None

    if isinstance(ctx.data, str) and ctx.data.startswith('/'):
        command = ctx.data.lstrip("/")

    state_obj.handle_message(command, **kwargs)
