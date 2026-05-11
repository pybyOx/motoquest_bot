from __future__ import annotations
from states.base_state import BaseUserState
from core.enums.user_states import UserState
from core.enums.callback_types import CallBackType
from keyboards import commands_for_player, commands_for_admin
from typing import TYPE_CHECKING, Callable, Any

if TYPE_CHECKING:
    from core.dto.context import Context
    from database.models.user import User


class IDLEState(BaseUserState):

    def __init__(self, services):
        super().__init__(services)
        self._callback_handlers = {
            CallBackType.START: self.handle_start_command,

            CallBackType.INFO: self.handle_info_command,
            CallBackType.HELP: self.handle_help_command,
            CallBackType.CANCEL: self.handle_cancel_command,
            CallBackType.REGISTRATION: self.handle_registration_command,

            CallBackType.CREATE_SESSION: self.services.admin_handler.handle_create_session,
            CallBackType.MANAGE_SESSION: self.services.admin_handler.handle_manage_session,

            CallBackType.ANSWER_CORRECT: self.services.inspector_handler.handle_callback,
            CallBackType.ANSWER_WRONG: self.services.inspector_handler.handle_callback,

        }

    def render(self, user_id: int, notify_text: str | None = None) -> None:
        user: User = self._user.get_by_id(model_id=user_id)
        text = "Доступные команды:"
        if notify_text:
            text = f"{notify_text}\n\n{text}"
        keyboard = commands_for_admin() if user.is_admin else commands_for_player()
        self._ui.show_user_ui(
            user=user,
            text=text,
            keyboard=keyboard,
        )

    def handle_start_command(self, ctx: Context, **_: Any) -> None:
        self._user.update_by_id(ctx.user_id, ui_msg_id=None)
        self.render(ctx.user_id, f"Привет, {ctx.full_name}!")

    def handle_help_command(self, ctx: Context, **_: Any) -> None:
        self._state.transition_and_render(ctx.user_id, UserState.help)

    def handle_registration_command(self, ctx: Context, **_: Any) -> None:
        game_sessions = self._game_session.get_active()
        if not game_sessions.exists():
            self._ui.answer_callback(
                callback_id=ctx.callback_id,
                text="Нет игр для записи."
            )
            return
        self._state.transition_and_render(ctx.user_id, UserState.registration)

    def handle_cancel_command(self, ctx: Context, **_: Any) -> None:
        user_sessions = self._user_session.get_registered(user_id=ctx.user_id)
        if not user_sessions.exists():
            self._ui.answer_callback(
                callback_id=ctx.callback_id,
                text="Записей на игры не найдено."
            )
            return
        self._state.transition_and_render(ctx.user_id, UserState.cancel)

    def handle_info_command(self, ctx: Context, **_: Any) -> None:
        user_sessions = self._user_session.get_registered(user_id=ctx.user_id)
        if not user_sessions.exists():
            self._ui.answer_callback(
                callback_id=ctx.callback_id,
                text="Записей на игры не найдено."
            )
            return
        self._state.transition_and_render(ctx.user_id, UserState.info)

    def _handle_message(self, ctx: Context, **_: Any) -> None:
        self.render(ctx.user_id, "Воспользуйтесь доступными командами или напишите в поддержку.")

    @property
    def callback_handlers(self) -> dict[str, Callable[..., None]]:
        return self._callback_handlers
