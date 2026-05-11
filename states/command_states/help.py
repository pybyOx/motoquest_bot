from __future__ import annotations
from states.base_state import BaseUserState
from typing import TYPE_CHECKING, Callable, Any

if TYPE_CHECKING:
    from services.services import Services
    from database.models.user import User
    from core.dto.context import Context


class HelpState(BaseUserState):
    def __init__(self, services: Services):
        super().__init__(services)
        self._callback_handlers = {}

    def render(self, user_id: int, notify_text: str | None = None) -> None:
        user: User = self._user.get_by_id(model_id=user_id)
        self._ui.show_user_ui(
            user=user,
            text="🆘 Напишите, в чем проблема: ",
        )

    def _handle_message(self, ctx: Context, **_: Any) -> None:

        self._ui.send_player_problem(
            problem_msg=ctx.data,
            user_id=ctx.user_id,
            username=ctx.username,
            full_name=ctx.full_name
        )
        self._finish_action(ctx.user_id, "Ваше сообщение отправлено. Поддержка свяжется с вами в ближайшее время.")

    @property
    def callback_handlers(self) -> dict[str, Callable[..., None]]:
        return self._callback_handlers
