from enum import StrEnum


class UserEventType(StrEnum):
    START_MESSAGE_SENT = "start_message_sent"
    CANCEL_MESSAGE_SENT = "cancel_message_sent"
