from __future__ import annotations
from database.db import db
from core.enums.callback_types import CallBackType
from keyboards import combine_keyboards, objects_keyboard, cancel_or_back_keyboard
from states.base_state import BaseUserState
from core.enums.user_states import UserState
from presenters.telegram.build_keyboard_items import build_keyboard_items
from typing import TYPE_CHECKING, Callable, Any

if TYPE_CHECKING:
    from database.models.game_session import GameSession
    from database.models.user import User
    from core.dto.context import Context


class SessionChoiceState(BaseUserState):

    def __init__(self, services):
        super().__init__(services)
        self._callback_handlers = {
            CallBackType.CANCEL_ACTION: self.handle_cancel_action,
            CallBackType.CHOSEN_SESSION: self.handle_chosen_session,
        }

    def render(self, user_id: int, notify_text: str | None = None) -> None:
        game_sessions = self._game_session.get_active()
        user: User = self._user.get_by_id(model_id=user_id)

        text = "Выберите игровую сессию, которой хотите управлять:"
        if notify_text:
            text = f"{notify_text}\n\n{text}"

        self._ui.show_user_ui(
            user=user,
            text=text,
            keyboard=combine_keyboards(
                objects_keyboard(
                    objects=build_keyboard_items(game_sessions),
                    callback_data=f"{CallBackType.CHOSEN_SESSION}"
                ),
                cancel_or_back_keyboard(prev_func=False)
            ),
        )

    def handle_chosen_session(self, ctx: Context, payload: str, **_: Any) -> None:
        game_session: GameSession = self._game_session.get_by_id(model_id=int(payload))
        with db.atomic():
            self._draft.update_by_id(ctx.user_id, game_session=game_session)
            self._state.transition(ctx.user_id, UserState.choice_action)
        self._state.render(ctx.user_id, UserState.choice_action)

    def _handle_message(self, ctx: Context, **_: Any) -> None:
        self.render(ctx.user_id, "Нажмите кнопку, чтобы выбрать игровую сессию.")

    @property
    def callback_handlers(self) -> dict[str, Callable[..., None]]:
        return self._callback_handlers
