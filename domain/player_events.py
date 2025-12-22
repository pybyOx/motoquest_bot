from repositories.repositories import PlayerEventRepository
from typing import Callable


def do_event_once(player_session, event_type: str, action: Callable[[], None]):
    """"""
    if PlayerEventRepository.exists(player_session, event_type):
        return False

    action()
    PlayerEventRepository.create(player_session=player_session,
                                 event_type=event_type)
    return True
