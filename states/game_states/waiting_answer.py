from __future__ import annotations
from database.db import db
from core.enums.callback_types import CallBackType
from core.enums.user_states import UserState
from core.utils.check_content import is_allowed_answer_content
from keyboards import get_clue_keyboard
from config_data.config import GAMES_DATA_DIR
from states.base_state import BaseUserState
from typing import TYPE_CHECKING, Callable, Any


if TYPE_CHECKING:
    from database.models.user import User
    from core.dto.context import Context
    from services.services import Services


class WaitingAnswerState(BaseUserState):
    def __init__(self, services: Services):
        super().__init__(services)
        self._callback_handlers = {
            CallBackType.GET_CLUE: self.handle_get_clue,
        }

    def render(self, user_id: int, notify_text: str | None = None) -> None:
        user: User = self._user.get_by_id(model_id=user_id)
        current_point, point_progress = self._guard.require_point_and_progress(user)
        clues_used = point_progress.clues_used
        clues_left = 3 - clues_used
        clues = self.services.clue_repo.get_clues_up_to(
            point_id=current_point.id,
            max_order=clues_used
        )
        self._ui.send_info(
            chat_id=user_id,
            game_dir=GAMES_DATA_DIR / user.current_user_session.game_session.game_info.slug,
            info=current_point.task,
            msg_ids=point_progress.task_msg_ids or {},
            repo=self.services.point_progress_repo,
            obj_id=point_progress.id,
            obj_field="task_msg_ids"
        )

        text = "Ответ неверный. Попробуйте еще раз."\
            if point_progress.answer_error \
            else "Отправьте ответ на задание."
        if notify_text:
            text = f"{notify_text}\n\n{text}"
        keyboard = None

        for clue in clues:
            text += f"\n\nПодсказка №{clue.order}:\n{clue.text}"

        if clues_left > 0:
            text += f"\n\nЕсли возникнут сложности — воспользуйтесь подсказкой.\n(осталось: {clues_left})"
            keyboard = get_clue_keyboard()

        self._ui.show_user_ui(
            user=user,
            text=text,
            keyboard=keyboard
        )

    def _handle_message(self, ctx: Context, **_: Any) -> None:
        user: User = self._user.get_by_id(ctx.user_id)
        current_point, point_progress = self._guard.require_point_and_progress(ctx.user)

        if is_allowed_answer_content(content_type=ctx.content_type, answer=ctx.data):
            self._ui.send_player_answer(
                chat_id=ctx.chat_id,
                msg_id=ctx.message_id,
                user_str=f"{user}",
                point=current_point,
                point_progress_id=point_progress.id,
            )
            with db.atomic():
                self._point_progress.update_by_id(point_progress.id, answer_error=False)
                self._state.transition(ctx.user_id, UserState.waiting_review)
            self._state.render(ctx.user_id, UserState.waiting_review)
        else:
            self.render(ctx.user_id, "В качестве ответа принимаются текст или фото.")

    def handle_get_clue(self, ctx: Context, **_: Any) -> None:
        _, point_progress = self._guard.require_point_and_progress(ctx.user)

        new_clues_used = self._point_progress.increment_clues_used(point_progress.id)
        if new_clues_used is None:
            return

        self.render(ctx.user_id)

    @property
    def callback_handlers(self) -> dict[str, Callable[..., None]]:
        return self._callback_handlers
