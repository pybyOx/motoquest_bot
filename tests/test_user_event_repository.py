from core.enums.user_event_types import UserEventType
from database.models.user_event import UserEvent


# ── create_once ───────────────────────────────────────────────────────────────

def test_create_once_creates_event(user_event_repo, user_session):
    result = user_event_repo.create_once(user_session.id, UserEventType.START_MESSAGE_SENT)

    assert result is True
    assert UserEvent.select().count() == 1


def test_create_once_returns_false_for_duplicate_event(user_event_repo, user_session):
    user_event_repo.create_once(user_session.id, UserEventType.START_MESSAGE_SENT)

    result = user_event_repo.create_once(user_session.id, UserEventType.START_MESSAGE_SENT)

    assert result is False
    assert UserEvent.select().count() == 1


def test_create_once_creates_two_events_for_different_event_types(user_event_repo, user_session):
    result_1 = user_event_repo.create_once(user_session.id, UserEventType.START_MESSAGE_SENT)
    result_2 = user_event_repo.create_once(user_session.id, UserEventType.CANCEL_MESSAGE_SENT)

    assert result_1 is True
    assert result_2 is True
    assert UserEvent.select().count() == 2


def test_create_once_creates_two_events_for_different_sessions(
        user_event_repo, user_session, other_user_session,
):
    result_1 = user_event_repo.create_once(user_session.id, UserEventType.START_MESSAGE_SENT)
    result_2 = user_event_repo.create_once(other_user_session.id, UserEventType.START_MESSAGE_SENT)

    assert result_1 is True
    assert result_2 is True
    assert UserEvent.select().count() == 2
