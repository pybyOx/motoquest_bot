from __future__ import annotations
import logging
from core.enums.user_states import UserState
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.user import User
    from database.repositories.user_repository import UserRepository
    from states.factory import StateFactory


class UserStatesService:
    def __init__(
            self,
            user_repo: UserRepository,
            states_factory: StateFactory = None,
    ):
        self.user_repo = user_repo
        self.states_factory = states_factory

    ALLOWED_TRANSITIONS: dict[UserState, list[UserState]] = {
        UserState.idle: [
            UserState.idle,
            UserState.info,
            UserState.help,
            UserState.cancel,
            UserState.registration,
            UserState.choice_game,
            UserState.choice_session,
            UserState.waiting_location,
        ],


        UserState.waiting_location: [
            UserState.waiting_location,
            UserState.waiting_arrive,
            UserState.idle
        ],
        UserState.waiting_arrive: [
            UserState.waiting_arrive,
            UserState.waiting_answer
        ],
        UserState.waiting_answer: [
            UserState.waiting_answer,
            UserState.waiting_review
        ],
        UserState.waiting_review: [
            UserState.waiting_review,
            UserState.waiting_location,
            UserState.waiting_answer,
            UserState.idle,
        ],


        UserState.choice_game: [
            UserState.choice_game,
            UserState.choice_city,
            UserState.idle,
        ],
        UserState.choice_city: [
            UserState.choice_game,
            UserState.choice_city,
            UserState.choice_location,
            UserState.idle,
        ],
        UserState.choice_location: [
            UserState.choice_city,
            UserState.choice_location,
            UserState.choice_date,
            UserState.idle,
        ],
        UserState.choice_date: [
            UserState.choice_location,
            UserState.choice_date,
            UserState.confirmation,
            UserState.idle,
        ],
        UserState.confirmation: [
            UserState.choice_date,
            UserState.confirmation,
            UserState.idle,
        ],

        UserState.choice_session: [
            UserState.choice_session,
            UserState.choice_action,
            UserState.idle,
        ],
        UserState.choice_action: [
            UserState.choice_session,
            UserState.choice_action,
            UserState.idle,
        ],


        UserState.cancel: [
            UserState.cancel,
            UserState.idle,
        ],
        UserState.info: [
            UserState.info,
            UserState.idle,
        ],
        UserState.registration: [
            UserState.registration,
            UserState.idle,
        ],
        UserState.help: [
            UserState.help,
            UserState.idle,
        ],
    }

    def set_state_factory(self, states_factory: StateFactory) -> None:
        self.states_factory = states_factory

    def transition(self, user_id: int, new_state: UserState) -> None:
        user: User = self.user_repo.get_by_id(user_id)
        current_state = UserState(user.state)
        allowed = self.ALLOWED_TRANSITIONS.get(current_state, [])

        if new_state not in allowed:
            error_text = f"[{user_id}]: Invalid FSM transition <{current_state}> → <{new_state}>"
            logging.warning(error_text)
            raise Exception(error_text)

        self.user_repo.update_state(user_id=user_id, state=new_state)
        logging.info(f"[{user_id}]: FSM transition <{current_state}> → <{new_state}>")

    def render(self, user_id: int, state: UserState, notify_text: str | None = None) -> None:
        self.states_factory.get(state).render(user_id, notify_text)

    def transition_and_render(self, user_id: int, new_state: UserState) -> None:
        self.transition(user_id, new_state)
        self.render(user_id, new_state)

    def recover(self, user_id: int, notify_text: str | None = None):
        user: User = self.user_repo.get_by_id(model_id=user_id)
        self.states_factory.get(state=UserState(user.state)).render(user_id, notify_text)
        logging.info(f"[{user_id}]: recovery from {user.state} state")
        self.user_repo.clear_error(user_id)
