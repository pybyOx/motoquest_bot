from __future__ import annotations
from .game_states.waiting_location import WaitingLocationState
from .game_states.waiting_arrive import WaitingArriveState
from .game_states.waiting_answer import WaitingAnswerState
from .game_states.waiting_review import WaitingReviewState
from .idle import IDLEState
from .admin_states.manage_session_states.action_choice import ActionChoiceState
from .admin_states.manage_session_states.attendance_check import AttendanceCheckState
from .admin_states.manage_session_states.session_choice import SessionChoiceState
from .admin_states.creation_session_states.city_choice import CityChoiceState
from .admin_states.creation_session_states.date_choice import DateChoiceState
from .admin_states.creation_session_states.game_choice import GameChoiceState
from .admin_states.creation_session_states.location_choice import LocationChoiceState
from states.admin_states.creation_session_states.confirmation_create import CreateConfirmationState
from .command_states.registration import RegistrationState
from .command_states.cancel import CancelState
from .command_states.info import InfoState
from .command_states.help import HelpState
from core.enums.user_states import UserState
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from states.base_state import BaseUserState


class StateFactory:
    def __init__(self, services):
        self.services = services
        self.mapping = {
            UserState.idle: IDLEState,

            UserState.waiting_location: WaitingLocationState,
            UserState.waiting_arrive: WaitingArriveState,
            UserState.waiting_answer: WaitingAnswerState,
            UserState.waiting_review: WaitingReviewState,

            UserState.registration: RegistrationState,
            UserState.cancel: CancelState,
            UserState.info: InfoState,
            UserState.help: HelpState,

            UserState.choice_game: GameChoiceState,
            UserState.choice_city: CityChoiceState,
            UserState.choice_location: LocationChoiceState,
            UserState.choice_date: DateChoiceState,

            UserState.choice_session: SessionChoiceState,
            UserState.choice_action: ActionChoiceState,
            UserState.attendance_check: AttendanceCheckState,

            UserState.confirmation: CreateConfirmationState,
        }

    def get(self, state: UserState) -> BaseUserState:
        try:
            return self.mapping[state](self.services)
        except KeyError:
            raise ValueError(f"No state class for {state}")
