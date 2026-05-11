from __future__ import annotations
from core.enums.user_states import UserState
from core.enums.callback_types import CallBackType
from database.db import db
from keyboards import arrived_keyboard
from states.base_state import BaseUserState
from config_data.config import GAMES_DATA_DIR
from presenters.telegram.html import bold
from typing import Any, TYPE_CHECKING, Callable


if TYPE_CHECKING:
    from database.models.user import User
    from core.dto.context import Context
    from services.services import Services


class WaitingArriveState(BaseUserState):

    def __init__(self, services: Services):
        super().__init__(services)
        self._callback_handlers = {
            CallBackType.ARRIVED: self.handle_arrived,
        }

    def render(self, user_id: int, notify_text: str | None = None) -> None:
        user: User = self._user.get_by_id(model_id=user_id)
        current_point, point_progress = self._guard.require_point_and_progress(user)
        location_info: dict = current_point.location
        self._ui.send_info(
            chat_id=user_id,
            game_dir=GAMES_DATA_DIR / user.current_user_session.game_session.game_info.slug,
            info=location_info,
            msg_ids=point_progress.location_msg_ids or {},
            repo=self.services.point_progress_repo,
            obj_id=point_progress.id,
            obj_field="location_msg_ids",
            is_location=True
        )
        text = "Когда прибудете на место, нажмите:"
        if notify_text:
            text = f"{notify_text}\n\n{text}"
        self._ui.show_user_ui(
            user=user,
            text=text,
            keyboard=arrived_keyboard()
        )

    def handle_arrived(self, ctx: Context, **_: Any) -> None:
        current_point, point_progress = self._guard.require_point_and_progress(ctx.user)

        self._ui.show_user_ui(
            user=ctx.user,
            text=f"Вы прибыли на точку {bold(current_point.title)}",
            parse_mode="HTML"
        )
        with db.atomic():
            self._point_progress.start_progress(point_progress.id)
            self._reset_user_ui(ctx.user_id)
            self._state.transition(ctx.user_id, UserState.waiting_answer)
        self._state.render(ctx.user_id, UserState.waiting_answer)

    def _handle_message(self, ctx: Context, **_: Any) -> None:
        self.render(ctx.user_id, "Нажмите кнопку «Я на месте», чтобы получить задание.")

    @property
    def callback_handlers(self) -> dict[str, Callable[..., None]]:
        return self._callback_handlers
