from __future__ import annotations
from core.exceptions import AlreadyExistsError
from core.enums.callback_types import CallBackType
from keyboards import objects_keyboard
from presenters.telegram.render_location import render_location
from presenters.telegram.build_keyboard_items import build_keyboard_items
from states.base_state import BaseUserState
from typing import TYPE_CHECKING, Callable, Any


if TYPE_CHECKING:
    from core.dto.context import Context
    from database.models.user import User
    from services.services import Services


class RegistrationState(BaseUserState):
    def __init__(self, services: Services):
        super().__init__(services)
        self._callback_handlers = {
            CallBackType.REGISTRATION_GAME_SESSION: self.handle_registration_game_session,
        }

    def render(self, user_id: int, notify_text: str | None = None) -> None:
        user: User = self._user.get_by_id(model_id=user_id)
        game_sessions = self._game_session.get_active()
        text = "Выберите игру, на которую хотите записаться:"
        if notify_text:
            text = f"{notify_text}\n\n{text}"
        self._ui.show_user_ui(
            user=user,
            text=text,
            keyboard=objects_keyboard(
                objects=build_keyboard_items(game_sessions),
                callback_data=f"{CallBackType.REGISTRATION_GAME_SESSION}"
            ),
        )

    def handle_registration_game_session(self, ctx: Context, payload: str, **_: Any) -> None:
        session_id = int(payload)
        game_session = self._game_session.get_by_id(model_id=session_id)
        try:
            self._user_session.create(data=dict(user=ctx.user, game_session=game_session))
        except AlreadyExistsError:
            text = "✅Вы уже записаны"
        else:
            text = "✅Вы успешно записаны"
        self._ui.show_user_ui(
            user=ctx.user,
            text=f"{text} на игру\n{game_session}\n{render_location(game_session.location)}",
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        self._reset_user_ui(ctx.user_id)
        self._finish_action(ctx.user_id)

    def _handle_message(self, ctx: Context, **_: Any) -> None:
        self.render(ctx.user_id, "Нажмите кнопку, чтобы выбрать игру, на которую хотите записаться.")

    @property
    def callback_handlers(self) -> dict[str, Callable[..., None]]:
        return self._callback_handlers
