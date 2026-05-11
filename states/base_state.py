from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from core.enums.user_states import UserState
from typing import TYPE_CHECKING, Callable, Any


if TYPE_CHECKING:
    from core.dto.context import Context
    from services.game_guard import GameGuard
    from services.services import Services
    from services.ui_service import UIService
    from database.repositories.admin_draft_repository import AdminDraftRepository
    from database.repositories.user_repository import UserRepository
    from database.repositories.user_session_repository import UserSessionRepository
    from database.repositories.point_progress_repository import PointProgressRepository
    from database.repositories.game_session_repository import GameSessionRepository
    from services.states_services.user_states_service import UserStatesService


class BaseUserState(ABC):
    def __init__(self, services: Services):
        self.services = services

    @property
    @abstractmethod
    def callback_handlers(self) -> dict[str, Callable[..., None]]:
        ...

    @property
    def allowed_callbacks_or_commands(self) -> set[str]:
        return set(self.callback_handlers.keys())

    @property
    def _state(self) -> UserStatesService:
        return self.services.user_states_service

    @property
    def _ui(self) -> UIService:
        return self.services.ui

    @property
    def _guard(self) -> GameGuard:
        return self.services.game_guard

    @property
    def _draft(self) -> AdminDraftRepository:
        return self.services.admin_draft_repo

    @property
    def _user(self) -> UserRepository:
        return self.services.user_repo

    @property
    def _user_session(self) -> UserSessionRepository:
        return self.services.user_session_repo

    @property
    def _point_progress(self) -> PointProgressRepository:
        return self.services.point_progress_repo

    @property
    def _game_session(self) -> GameSessionRepository:
        return self.services.game_session_repo

    def can_handle(self, callback_or_command_type: str) -> bool:
        return callback_or_command_type in self.allowed_callbacks_or_commands

    @abstractmethod
    def render(self, user_id: int, notify_text: str | None = None) -> None:
        pass

    def handle_message(self, command: str | None = None, **kwargs):
        ctx: Context = kwargs["ctx"]

        try:
            self._ui.delete_ui_keyboard(ctx.chat_id, ctx.user.ui_msg_id)
        except Exception as error:
            logging.error(f"Не удалось удалить клавиатуру: {error}")

        self._reset_user_ui(ctx.user_id)

        if command:
            if not self.can_handle(command):
                logging.warning(f"Unexpected command {command} for state {ctx.user_state}", )

                self._state.render(
                    user_id=ctx.user_id,
                    state=ctx.user_state,
                    notify_text="Чтобы воспользоваться командой, завершите или отмените текущее действие."
                )
                return
            handler = self.callback_handlers.get(command)
            if handler is None:
                raise ValueError(f"{self.__class__.__name__}: unsupported command {command}")
            handler(**kwargs)
            return

        return self._handle_message(**kwargs)

    @abstractmethod
    def _handle_message(self, **kwargs) -> None:
        pass

    def handle_callback(self, **kwargs) -> None:
        callback_type = kwargs["callback_type"]
        handler = self.callback_handlers.get(callback_type)

        if handler is None:
            raise ValueError(f"{self.__class__.__name__}: unsupported callback {callback_type}")

        handler(**kwargs)

    BACK_TRANSITIONS: dict[UserState, UserState] = {
        UserState.choice_city: UserState.choice_game,
        UserState.choice_location: UserState.choice_city,
        UserState.choice_date: UserState.choice_location,
        UserState.confirmation: UserState.choice_date,
        UserState.choice_action: UserState.choice_session,
    }

    def handle_back(self, ctx: Context, **_: Any) -> None:
        """Переводит в состояние, предшествующее текущему и отображает его UI."""
        prev_state: UserState = self.BACK_TRANSITIONS.get(ctx.user_state, None)
        if prev_state:
            self._state.transition(ctx.user_id, prev_state)
            self._state.render(ctx.user_id, prev_state)

    def handle_cancel_action(self, ctx: Context, **_: Any) -> None:
        self._finish_admin_action(ctx.user_id, "🚫 Действие отменено")

    def _finish_admin_action(self, user_id: int, notify_text: str) -> None:
        """
        Очищает параметры action_draft.
        Переводит в idle state и отображает его UI с оповещением notify_text.
        """
        self._draft.reset_all(user_id)
        self._finish_action(user_id, notify_text)

    def _finish_action(self, user_id: int, notify_text: str | None = None) -> None:
        """
        Переводит в idle state и отображает его UI с оповещением notify_text.
        """
        self._state.transition(user_id, UserState.idle)
        self._state.render(
            user_id=user_id,
            state=UserState.idle,
            notify_text=notify_text,
        )

    def _reset_user_ui(self, user_id: int) -> None:
        self._user.reset_ui_msg_id(user_id)
