from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from database.repositories.clue_repository import ClueRepository
    from database.repositories.game_info_repository import GameInfoRepository
    from database.repositories.game_session_repository import GameSessionRepository
    from database.repositories.user_event_repository import UserEventRepository
    from database.repositories.user_session_repository import UserSessionRepository
    from database.repositories.point_progress_repository import PointProgressRepository
    from database.repositories.point_repository import PointRepository
    from database.repositories.user_repository import UserRepository
    from database.repositories.admin_draft_repository import AdminDraftRepository
    from services.states_services.user_states_service import UserStatesService
    from services.ui_service import UIService
    from services.game_guard import GameGuard
    from services.admin_handler import AdminHandler
    from services.inspector_handler import InspectorHandler


class Services:
    def __init__(
        self,
        ui_service: UIService,
        clue_repo: ClueRepository,
        game_info_repo: GameInfoRepository,
        game_session_repo: GameSessionRepository,
        user_event_repo: UserEventRepository,
        user_session_repo: UserSessionRepository,
        point_progress_repo: PointProgressRepository,
        point_repo: PointRepository,
        user_repo: UserRepository,
        admin_draft_repo: AdminDraftRepository,
        user_states_service: UserStatesService,
        game_guard: GameGuard,
        admin_handler: AdminHandler,
        inspector_handler: InspectorHandler,
    ):
        self.ui = ui_service
        self.clue_repo = clue_repo
        self.game_info_repo = game_info_repo
        self.game_session_repo = game_session_repo
        self.user_event_repo = user_event_repo
        self.user_session_repo = user_session_repo
        self.point_progress_repo = point_progress_repo
        self.point_repo = point_repo
        self.user_repo = user_repo
        self.admin_draft_repo = admin_draft_repo
        self.user_states_service = user_states_service
        self.game_guard = game_guard
        self.admin_handler = admin_handler
        self.inspector_handler = inspector_handler
