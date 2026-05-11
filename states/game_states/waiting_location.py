from __future__ import annotations
from states.base_state import BaseUserState
from keyboards import objects_keyboard
from core.enums.callback_types import CallBackType
from database.db import db
from core.enums.user_states import UserState
from presenters.telegram.build_keyboard_items import build_point_progresses_keyboard_items
from typing import Any, TYPE_CHECKING, Callable


if TYPE_CHECKING:
    from database.models.user import User
    from database.models.point import Point
    from database.models.user_session import UserSession
    from core.dto.context import Context
    from services.services import Services


class WaitingLocationState(BaseUserState):
    def __init__(self, services: Services):
        super().__init__(services)
        self._callback_handlers = {
            CallBackType.CHOSEN_LOCATION: self.handle_chosen_location,
        }

    def render(self, user_id: int, notify_text: str | None = None) -> None:
        user: User = self._user.get_by_id(model_id=user_id)
        user_session: UserSession = self._guard.require_user_session(user)
        non_finished = self._point_progress.get_non_finished_by_session(
            user_session_id=user_session.id
        )
        text = "Выберите локацию:"
        if notify_text:
            text = f"{notify_text}\n\n{text}"

        self._ui.show_user_ui(
            user=user,
            text=text,
            keyboard=objects_keyboard(
                objects=build_point_progresses_keyboard_items(non_finished),
                callback_data=f"{CallBackType.CHOSEN_LOCATION}"
            ),
        )

    def handle_chosen_location(
            self,
            ctx: Context,
            payload: str,
            **_: Any
    ) -> None:
        user_session: UserSession = self._guard.require_user_session(ctx.user)
        point_id: int = int(payload)
        point: Point = self.services.point_repo.get_by_id(model_id=point_id)

        with db.atomic():
            self._user_session.set_current_point(
                user_session_id=user_session.id,
                point_id=point_id
            )
            self._state.transition(ctx.user_id, UserState.waiting_arrive)
        self._state.render(ctx.user_id, UserState.waiting_arrive,
                           notify_text=f"Пункт назначения - {point.title}")

    def _handle_message(self, ctx: Context, **_: Any) -> None:
        self.render(ctx.user_id, "Нажмите кнопку, чтобы выбрать локацию.")

    @property
    def callback_handlers(self) -> dict[str, Callable[..., None]]:
        return self._callback_handlers
