from enum import StrEnum


class UserState(StrEnum):
    idle = "idle"

    waiting_location = "waiting_location"
    waiting_arrive = "waiting_arrive"
    waiting_answer = "waiting_answer"
    waiting_review = "waiting_review"

    registration = "registration"
    cancel = "cancel"
    info = "info"
    help = "help"

    choice_game = "choice_game"
    choice_city = "choice_city"
    choice_location = "choice_location"
    choice_date = "choice_date"

    choice_session = "choice_session"
    choice_action = "choice_action"

    confirmation = "confirmation"
