from __future__ import annotations
from database.db import db
from core.enums.user_states import UserState
from states.base_state import BaseUserState
from presenters.telegram.render_location import render_location
from typing import TYPE_CHECKING, Callable, Any

if TYPE_CHECKING:
    from database.models.user import User
    from services.services import Services
    from database.models.game_session import GameSession


class InfoState(BaseUserState):
    def __init__(self, services: Services):
        super().__init__(services)
        self._callback_handlers = {}

    def render(self, user_id: int, notify_text: str | None = None) -> None:
        user_sessions = self._user_session.get_registered(user_id=user_id)
        user: User = self._user.get_by_id(model_id=user_id)

        lines = ["<b>Вы записаны на:</b>"]
        for us in user_sessions:
            game_session: GameSession = us.game_session
            lines.append(f"{game_session}\n{render_location(game_session.location)}")

        self._ui.show_user_ui(
            user=user,
            text="\n\n".join(lines),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        with db.atomic():
            self._reset_user_ui(user_id)
            self._state.transition(user_id, UserState.idle)
        self._state.render(user_id, UserState.idle)

    def _handle_message(self, **_: Any) -> None:
        pass

    @property
    def callback_handlers(self) -> dict[str, Callable[..., None]]:
        return self._callback_handlers
