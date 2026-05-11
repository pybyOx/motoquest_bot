from __future__ import annotations
from database.db import db
from core.enums.callback_types import CallBackType
from core.enums.user_states import UserState
from config_data.config import GAMES_DATA_DIR
from typing import Any, TYPE_CHECKING


if TYPE_CHECKING:
    from database.models.user import User
    from database.models.user_session import UserSession
    from database.models.game_session import GameSession
    from database.models.point_progress import PointProgress
    from database.repositories.game_session_repository import GameSessionRepository
    from database.repositories.user_repository import UserRepository
    from database.repositories.user_session_repository import UserSessionRepository
    from database.repositories.point_progress_repository import PointProgressRepository
    from services.states_services.user_states_service import UserStatesService
    from core.dto.context import Context
    from services.game_guard import GameGuard
    from services.ui_service import UIService


class InspectorHandler:
    def __init__(
            self,
            game_session_repo: GameSessionRepository,
            user_repo: UserRepository,
            user_session_repo: UserSessionRepository,
            point_progress_repo: PointProgressRepository,
            user_states_service: UserStatesService,
            game_guard: GameGuard,
            ui: UIService,
    ):
        self.game_session_repo = game_session_repo
        self.user_repo = user_repo
        self.user_session_repo = user_session_repo
        self.point_progress_repo = point_progress_repo
        self.user_states_service = user_states_service
        self.game_guard = game_guard
        self.ui = ui

        self._callback_handlers = {
            CallBackType.ANSWER_CORRECT: self.handle_answer_correct,
            CallBackType.ANSWER_WRONG: self.handle_answer_wrong,
        }

    def handle_callback(self, ctx: Context, callback_type: str, payload: str, **_: Any) -> None:

        handler = self._callback_handlers.get(CallBackType(callback_type))
        if handler is None:
            raise ValueError(f"{self.__class__.__name__}: unsupported callback {callback_type}")

        point_progress: PointProgress = self.point_progress_repo.get_by_id(model_id=int(payload))
        if point_progress.is_finished:
            return

        user: User = point_progress.user_session.user
        if user.state != UserState.waiting_review:
            return

        handler(user=user, point_progress=point_progress)
        self.ui.delete_ui_keyboard(ctx.chat_id, ctx.message_id)
        self.ui.send_msg(
            chat_id=ctx.chat_id,
            text=callback_type,
            reply_to_message_id=ctx.message_id,
        )

    def handle_answer_correct(self, user: User, point_progress: PointProgress, **_: Any) -> None:
        user_id: int = user.id
        self.point_progress_repo.finish_progress(point_progress.id)
        after_solved_info: dict = point_progress.point.after_solved
        self.ui.send_info(
            chat_id=user_id,
            game_dir=GAMES_DATA_DIR / user.current_user_session.game_session.game_info.slug,
            info=after_solved_info,
            msg_ids=point_progress.solved_msg_ids or {},
            repo=self.point_progress_repo,
            obj_id=point_progress.id,
            obj_field="solved_msg_ids"
        )
        user_session: UserSession = self.game_guard.require_user_session(user)

        if not self.point_progress_repo.has_non_finished(user_session.id):
            game_session: GameSession = user_session.game_session
            finish_location_info: dict = game_session.game_info.finish
            self.ui.send_info(
                chat_id=user_id,
                game_dir=GAMES_DATA_DIR / game_session.game_info.slug,
                info=finish_location_info,
                msg_ids=user_session.finish_msg_ids or {},
                repo=self.user_session_repo,
                obj_id=user_session.id,
                obj_field="finish_msg_ids",
                is_location=True
            )
            with db.atomic():
                self.user_session_repo.finish_session(user_session.id)
                self.user_repo.update_by_id(user_id, ui_msg_id=None)
                self._state.transition(user_id, UserState.idle)
            self._state.render(user_id, UserState.idle)

            if not self.user_session_repo.has_non_finished(game_session.id):
                self.game_session_repo.set_finished(game_session.id)

            return

        with db.atomic():
            self.user_repo.update_by_id(user_id, ui_msg_id=None)
            self._state.transition(user_id, UserState.waiting_location)
        self._state.render(user_id, UserState.waiting_location)

    def handle_answer_wrong(self, user: User, point_progress: PointProgress, **_: Any) -> None:

        self.point_progress_repo.update_by_id(
            model_id=point_progress.id,
            answer_error=True
        )
        self._state.transition_and_render(user.id, UserState.waiting_answer)

    @property
    def _state(self) -> UserStatesService:
        return self.user_states_service
