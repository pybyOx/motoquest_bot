from __future__ import annotations
from keyboards import objects_keyboard
from core.enums.callback_types import CallBackType
from presenters.telegram.build_keyboard_items import build_keyboard_items
from states.base_state import BaseUserState
from typing import TYPE_CHECKING, Callable, Any


if TYPE_CHECKING:
    from core.dto.context import Context
    from database.models.user import User
    from services.services import Services


class CancelState(BaseUserState):
    def __init__(self, services: Services):
        super().__init__(services)
        self._callback_handlers = {
            CallBackType.CANCEL_USER_SESSION: self.handle_cancel_user_session,
        }

    def render(self, user_id: int, notify_text: str | None = None) -> None:
        user: User = self._user.get_by_id(model_id=user_id)
        user_sessions = self._user_session.get_registered(user_id=user_id)
        text = "Выберите игру, на которую нужно отменить запись:"
        if notify_text:
            text = f"{notify_text}\n\n{text}"
        self._ui.show_user_ui(
            user=user,
            text=text,
            keyboard=objects_keyboard(
                objects=build_keyboard_items(user_sessions),
                callback_data=f"{CallBackType.CANCEL_USER_SESSION}"
            ),
        )

    def handle_cancel_user_session(self, ctx: Context, payload: str, **_: Any) -> None:
        user_session = self._user_session.get_by_id(model_id=int(payload))
        self._user_session.delete_by_id(model_id=user_session.id)
        self._finish_action(ctx.user_id, f"✅ Запись на игру \n{user_session.game_session}\nуспешно отменена.")

    def _handle_message(self, ctx: Context, **_: Any) -> None:
        self.render(ctx.user_id, "Нажмите кнопку, чтобы выбрать игру, на которую нужно отменить запись.")

    @property
    def callback_handlers(self) -> dict[str, Callable[..., None]]:
        return self._callback_handlers
