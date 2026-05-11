from enum import StrEnum


class SessionState(StrEnum):
    REGISTERED = "registered"
    STARTED = "started"
    FINISHED = "finished"
