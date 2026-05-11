from __future__ import annotations
from database.db import db
from core.enums.user_states import UserState
from core.exceptions import AlreadyExistsError
from presenters.telegram.html import bold
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.dto.context import Context
    from database.repositories.user_repository import UserRepository
    from database.repositories.game_info_repository import GameInfoRepository
    from database.repositories.game_session_repository import GameSessionRepository
    from database.repositories.admin_draft_repository import AdminDraftRepository
    from services.states_services.user_states_service import UserStatesService
    from services.ui_service import UIService


class AdminHandler:
    def __init__(
            self,
            user_repo: UserRepository,
            game_info_repo: GameInfoRepository,
            game_session_repo: GameSessionRepository,
            user_states_service: UserStatesService,
            admin_draft_repo: AdminDraftRepository,
            ui: UIService,
    ):
        self.user_repo = user_repo
        self.game_info_repo = game_info_repo
        self.game_session_repo = game_session_repo
        self.user_states_service = user_states_service
        self.admin_draft_repo = admin_draft_repo
        self.ui = ui

    def handle_create_session(self, ctx: Context, **_: Any) -> None:
        games = self.game_info_repo.get_all()
        if not games.exists():
            self.ui.answer_callback(
                callback_id=ctx.callback_id,
                text="Созданных игр нет.",
            )
            return
        try:
            self.admin_draft_repo.create(dict(user_id=ctx.user_id))
        except AlreadyExistsError:
            self.admin_draft_repo.reset_all(ctx.user_id)
        self.ui.show_user_ui(
            user=ctx.user,
            text=bold("Создание сессии"),
            parse_mode="HTML"
        )
        with db.atomic():
            self.user_repo.reset_ui_msg_id(ctx.user_id)
            self.user_states_service.transition(ctx.user_id, new_state=UserState.choice_game)
        self.user_states_service.render(ctx.user_id, UserState.choice_game)

    def handle_manage_session(self, ctx: Context, **_: Any) -> None:
        game_sessions = self.game_session_repo.get_active()
        if not game_sessions.exists():
            self.ui.answer_callback(
                callback_id=ctx.callback_id,
                text="Нет активных игровых сессий.",
            )
            return
        try:
            self.admin_draft_repo.create(dict(user_id=ctx.user_id))
        except AlreadyExistsError:
            self.admin_draft_repo.reset_all(ctx.user_id)
        self.user_states_service.transition_and_render(ctx.user_id, UserState.choice_session)
