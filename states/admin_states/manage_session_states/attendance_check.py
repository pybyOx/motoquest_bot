from __future__ import annotations

import logging

from peewee import DoesNotExist

from database.db import db
from core.enums.callback_types import CallBackType
from core.enums.session_states import SessionState
from core.enums.user_states import UserState
from core.exceptions import AlreadyExistsError
from keyboards import attendance_keyboard
from states.base_state import BaseUserState
from typing import TYPE_CHECKING, Callable, Any

if TYPE_CHECKING:
    from database.models.game_session import GameSession
    from database.models.user import User
    from core.dto.context import Context


class AttendanceCheckState(BaseUserState):

    def __init__(self, services):
        super().__init__(services)
        self._callback_handlers = {
            CallBackType.CANCEL_ACTION: self.handle_cancel_action,
            CallBackType.MARK_ABSENT: self.handle_mark_absent,
            CallBackType.CONFIRM_ATTENDANCE: self.handle_confirm_attendance,
        }

    def render(self, user_id: int, notify_text: str | None = None) -> None:
        user: User = self._user.get_by_id(model_id=user_id)
        game_session: GameSession = self._draft.get_by_id(user_id).game_session
        registered = [us for us in game_session.user_sessions
                      if us.state == SessionState.REGISTERED]

        text = f"Игровая сессия: {game_session}\n\nОтметьте отсутствующих игроков:"
        if notify_text:
            text = f"{notify_text}\n\n{text}"

        self._ui.show_user_ui(
            user=user,
            text=text,
            keyboard=attendance_keyboard(registered),
        )

    def handle_mark_absent(self, ctx: Context, payload: str, **_: Any) -> None:
        try:
            self._user_session.delete_by_id(int(payload))
        except DoesNotExist:
            pass

        game_session: GameSession = self._draft.get_by_id(ctx.user_id).game_session
        remaining = [us for us in game_session.user_sessions
                     if us.state == SessionState.REGISTERED]

        if not remaining:
            self._finish_admin_action(
                ctx.user_id,
                "⚠️ Все игроки отмечены как отсутствующие. Игра не начата."
            )
            return

    def handle_confirm_attendance(self, ctx: Context, **_: Any) -> None:
        game_session: GameSession = self._draft.get_by_id(ctx.user_id).game_session
        registered = [us for us in game_session.user_sessions
                      if us.state == SessionState.REGISTERED]

        if not registered:
            self._finish_admin_action(ctx.user_id, "⚠️ Нет игроков для старта.")
            return

        try:
            for us in registered:
                user_id, user_session_id = us.user.id, us.id
                with db.atomic():
                    self._user.update_current_session(
                        user_id=user_id,
                        user_session_id=user_session_id
                    )
                    self._user_session.start_session(user_session_id=user_session_id)
                    self._point_progress.create_for_session(
                        user_session_id=user_session_id,
                        point_ids=[point.id for point in game_session.game_info.points]
                    )
                    self._state.transition(user_id, UserState.waiting_location)
                self._state.render(
                    user_id,
                    UserState.waiting_location,
                    f"{us.game_session}\nИгра началась!"
                )
        except AlreadyExistsError:
            text = f"⚠️ Игра {game_session} уже была начата или данные старта уже существуют."
        else:
            text = f"✅ Игра {game_session} успешно стартовала."
        self._finish_admin_action(ctx.user_id, text)

    def _handle_message(self, ctx: Context, **_: Any) -> None:
        self.render(ctx.user_id, "Нажмите кнопку, чтобы выбрать действие.")

    @property
    def callback_handlers(self) -> dict[str, Callable[..., None]]:
        return self._callback_handlers
