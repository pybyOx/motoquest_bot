from enum import StrEnum


class CallBackType(StrEnum):
    CANCEL_ACTION = "cancel_action"
    BACK = "back"

    GAME_INFO_CHOICE = "game_info_choice"
    CHOSEN_SESSION = "chosen_session"
    CITY_CHOICE = "city"

    CANCEL_USER_SESSION = "cancel_user_session"
    REGISTRATION_GAME_SESSION = "registration_game_session"

    ANSWER_CORRECT = "answer_correct"
    ANSWER_WRONG = "answer_wrong"

    CHOSEN_LOCATION = "chosen_location"
    ARRIVED = "arrived"
    GET_CLUE = "get_clue"

    START = "start"

    CREATE_SESSION = "create_session"
    CREATE_CONFIRM = "create_session_confirm"

    MANAGE_SESSION = "manage_session"

    START_SESSION = "start_session"
    DELETE_SESSION = "delete_session"
    MARK_ABSENT = "mark_absent"
    CONFIRM_ATTENDANCE = "confirm_attendance"

    REGISTRATION = "registration"
    CANCEL = "cancel"
    INFO = "info"
    HELP = "help"
