from telebot import TeleBot
from config_data import config

# repositories
from database.repositories.user_repository import UserRepository
from database.repositories.game_session_repository import GameSessionRepository
from database.repositories.clue_repository import ClueRepository
from database.repositories.game_info_repository import GameInfoRepository
from database.repositories.user_event_repository import UserEventRepository
from database.repositories.user_session_repository import UserSessionRepository
from database.repositories.point_progress_repository import PointProgressRepository
from database.repositories.point_repository import PointRepository
from database.repositories.admin_draft_repository import AdminDraftRepository

# services
from services.states_services.user_states_service import UserStatesService
from services.ui_service import UIService
from services.services import Services
from states.factory import StateFactory
from services.inspector_handler import InspectorHandler
from services.admin_handler import AdminHandler
from services.game_guard import GameGuard

_container = None


def get_container():
    global _container
    if _container is None:
        _container = Container()
    return _container


class Container:
    def __init__(self):
        # --- infra ---
        self.bot = TeleBot(token=config.BOT_TOKEN)

        # --- repositories ---
        self.user_repo = UserRepository()
        self.user_event_repo = UserEventRepository()
        self.user_session_repo = UserSessionRepository()
        self.game_info_repo = GameInfoRepository()
        self.game_session_repo = GameSessionRepository()
        self.point_progress_repo = PointProgressRepository()
        self.point_repo = PointRepository()
        self.clue_repo = ClueRepository()
        self.admin_draft_repo = AdminDraftRepository()

        # --- services ---
        self.user_states_service = UserStatesService(
            user_repo=self.user_repo,
        )

        self.ui_service = UIService(
            bot=self.bot,
            user_repo=self.user_repo,
        )

        self.game_guard = GameGuard(self.point_progress_repo)

        self.admin_handler = AdminHandler(
            user_repo=self.user_repo,
            game_info_repo=self.game_info_repo,
            game_session_repo=self.game_session_repo,
            user_states_service=self.user_states_service,
            admin_draft_repo=self.admin_draft_repo,
            ui=self.ui_service,
        )
        self.inspector_handler = InspectorHandler(
            game_session_repo=self.game_session_repo,
            user_repo=self.user_repo,
            user_session_repo=self.user_session_repo,
            point_progress_repo=self.point_progress_repo,
            user_states_service=self.user_states_service,
            game_guard=self.game_guard,
            ui=self.ui_service,
        )

        self.services = Services(
            ui_service=self.ui_service,
            user_repo=self.user_repo,
            user_event_repo=self.user_event_repo,
            user_session_repo=self.user_session_repo,
            game_info_repo=self.game_info_repo,
            game_session_repo=self.game_session_repo,
            point_progress_repo=self.point_progress_repo,
            point_repo=self.point_repo,
            clue_repo=self.clue_repo,
            user_states_service=self.user_states_service,
            admin_draft_repo=self.admin_draft_repo,
            game_guard=self.game_guard,
            admin_handler=self.admin_handler,
            inspector_handler=self.inspector_handler,
        )
        self.state_factory = StateFactory(self.services)

        self.user_states_service.set_state_factory(self.state_factory)
