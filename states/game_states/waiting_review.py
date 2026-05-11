from __future__ import annotations
from states.base_state import BaseUserState
from typing import Any, TYPE_CHECKING, Callable


if TYPE_CHECKING:
    from core.dto.context import Context
    from database.models.user import User
    from services.services import Services


class WaitingReviewState(BaseUserState):
    def __init__(self, services: Services):
        super().__init__(services)
        self._callback_handlers = {}

    def render(self, user_id: int, notify_text: str | None = None) -> None:
        user: User = self._user.get_by_id(model_id=user_id)
        self._ui.show_user_ui(
            user=user,
            text="Ваш ответ получен. Ожидайте проверки.",
        )

    def _handle_message(self, ctx: Context, **_: Any) -> None:
        pass

    @property
    def callback_handlers(self) -> dict[str, Callable[..., None]]:
        return self._callback_handlers
