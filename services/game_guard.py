from __future__ import annotations
from core.exceptions import GameInvariantError
from core.enums.session_states import SessionState
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.user import User
    from database.models.user_session import UserSession
    from database.models.point_progress import PointProgress
    from database.repositories.point_progress_repository import PointProgressRepository
    from database.models.point import Point


class GameGuard:
    def __init__(self, point_progress_repo: PointProgressRepository):
        self.point_progress_repo = point_progress_repo

    def require_user_session(self, user: User) -> UserSession:
        user_session = user.current_user_session

        if user_session is None:
            logging.warning(f"{user.id}: current user session is None")
            raise GameInvariantError(GameInvariantError.USER_SESSION_REQUIRED)

        if user_session.state == SessionState.FINISHED:
            logging.warning(f"{user.id}: current user session is finished")
            raise GameInvariantError(GameInvariantError.USER_SESSION_FINISHED)

        return user_session

    def require_point_and_progress(self, user: User) -> tuple[Point, PointProgress]:
        user_session = self.require_user_session(user)

        current_point = user_session.current_point
        if current_point is None:
            raise GameInvariantError(GameInvariantError.CURRENT_POINT_REQUIRED)

        point_progress = self.point_progress_repo.get_current_by_session(
            user_session=user_session
        )
        if point_progress is None:
            raise GameInvariantError(GameInvariantError.POINT_PROGRESS_REQUIRED)

        return current_point, point_progress
