from __future__ import annotations

import logging

from peewee import ModelSelect
from database.db import db
from core.enums.callback_types import CallBackType
from keyboards import combine_keyboards, cancel_or_back_keyboard, start_or_delete_keyboard
from states.base_state import BaseUserState
from core.enums.user_states import UserState
from core.exceptions import AlreadyExistsError
from core.enums.session_states import SessionState
from core.enums.user_event_types import UserEventType
from typing import TYPE_CHECKING, Callable, Any


if TYPE_CHECKING:
    from database.models.user import User
    from database.models.game_session import GameSession
    from core.dto.context import Context


class ActionChoiceState(BaseUserState):

    def __init__(self, services):
        super().__init__(services)
        self._callback_handlers = {
            CallBackType.CANCEL_ACTION: self.handle_cancel_action,
            CallBackType.BACK: self.handle_back,
            CallBackType.DELETE_SESSION: self.handle_chosen_action,
            CallBackType.START_SESSION: self.handle_chosen_action,
        }

    def render(self, user_id: int, notify_text: str | None = None) -> None:
        user: User = self._user.get_by_id(model_id=user_id)
        text = "Выберите действие:"
        if notify_text:
            text = f"{notify_text}\n\n{text}"

        self._ui.show_user_ui(
            user=user,
            text=text,
            keyboard=combine_keyboards(
                start_or_delete_keyboard(), 
                cancel_or_back_keyboard()
            ),
        )

    def handle_chosen_action(self, callback_type: str, ctx: Context, **_: Any) -> None:
        user_id: int = ctx.user_id
        game_session: GameSession = self._draft.get_by_id(user_id).game_session

        related_sessions: ModelSelect = game_session.user_sessions
        if not related_sessions.exists():
            self._finish_admin_action(user_id, "⚠️ Нет зарегистрированных игроков.")
            return

        if callback_type == CallBackType.START_SESSION:
            self.handle_start_session(user_id, game_session, related_sessions)
        elif callback_type == CallBackType.DELETE_SESSION:
            self.handle_delete_session(user_id, game_session, related_sessions)
        else:
            logging.warning(f"Unexpected callback {callback_type} for state {ctx.user_state}")

    def handle_start_session(self, admin_id: int, game_session: GameSession, related_sessions: ModelSelect) -> None:
        try:
            for us in related_sessions:

                user_id, user_session_id = us.user.id, us.id

                if us.state != SessionState.REGISTERED:
                    continue

                with db.atomic():
                    self._user.update_current_session(
                        user_id=user_id,
                        user_session_id=user_session_id
                    )
                    self._user_session.start_session(
                        user_session_id=user_session_id
                    )
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
            text = f"⚠️ Игра {game_session} уже была начата или данные старта (прогресс по точкам) уже существуют."
        else:
            text = f"✅ Игра {game_session} успешно стартовала."
        self._finish_admin_action(admin_id, text)

    def handle_delete_session(self, admin_id: int, game_session: GameSession, related_sessions: ModelSelect) -> None:

        self._game_session.delete_by_id(model_id=game_session.id)

        for us in related_sessions:

            user_id, user_session_id = us.user.id, us.id

            if us.state != SessionState.REGISTERED:
                continue

            if self.services.user_event_repo.create_once(
                    user_session_id=user_session_id,
                    event_type=UserEventType.CANCEL_MESSAGE_SENT
            ):
                self._ui.send_msg(
                    chat_id=user_id,
                    text=f"{us.game_session}\n⚠️ Игра, на которую вы были записаны, отменена."
                )
        self._finish_admin_action(admin_id, f"✅ Игра {game_session} успешно удалена.")

    def _handle_message(self, ctx: Context, **_: Any) -> None:
        self.render(ctx.user_id, "Нажмите кнопку, чтобы выбрать действие.")

    @property
    def callback_handlers(self) -> dict[str, Callable[..., None]]:
        return self._callback_handlers
