import pytest

from core.enums.session_states import SessionState

from database.models.user_session import UserSession
from database.models.game_session import GameSession


STATE_SETTERS = [
    # (method_name, target_state)
    ("start_session", SessionState.STARTED),
    ("finish_session", SessionState.FINISHED),
]


@pytest.mark.parametrize("method_name, target_state", STATE_SETTERS)
def test_state_setter_changes_state(
    user_session_repo, user_session,
    method_name, target_state,
):
    method = getattr(user_session_repo, method_name)

    updated_count = method(user_session.id)

    user_session_from_db = user_session_repo.get_by_id(user_session.id)
    assert updated_count == 1
    assert user_session_from_db.state == target_state


@pytest.mark.parametrize("method_name, target_state", STATE_SETTERS)
def test_state_setter_does_not_affect_other_sessions(
    user_session_repo, user_session, other_user_session,
    method_name, target_state,
):
    method = getattr(user_session_repo, method_name)

    method(user_session.id)

    other_session_from_db = user_session_repo.get_by_id(other_user_session.id)
    assert other_session_from_db.state == SessionState.REGISTERED


@pytest.mark.parametrize("method_name, target_state", STATE_SETTERS)
def test_state_setter_returns_zero_if_session_not_found(
    user_session_repo,
    method_name, target_state,
):
    method = getattr(user_session_repo, method_name)

    updated_count = method(999)

    assert updated_count == 0


def test_set_current_point_sets_point(user_session_repo, user_session, point):
    updated_count = user_session_repo.set_current_point(user_session.id, point.id)

    user_session_from_db = user_session_repo.get_by_id(user_session.id)
    assert updated_count == 1
    assert user_session_from_db.current_point.id == point.id


def test_set_current_point_does_not_affect_other_sessions(
    user_session_repo, user_session, other_user_session, point,
):
    user_session_repo.set_current_point(user_session.id, point.id)

    other_session_from_db = user_session_repo.get_by_id(other_user_session.id)
    assert other_session_from_db.current_point is None


def test_set_current_point_returns_zero_if_session_not_found(user_session_repo, point):
    updated_count = user_session_repo.set_current_point(999, point.id)

    assert updated_count == 0


def test_get_registered_returns_user_session_with_registered_state(user_session_repo, user, game_session):
    UserSession.create(user=user, game_session=game_session)

    result = user_session_repo.get_registered(user.id)

    assert result.count() == 1
    assert result.first().state == SessionState.REGISTERED


def test_get_registered_skips_sessions_with_other_states(user_session_repo, user, game_session):
    UserSession.create(user=user, game_session=game_session, state=SessionState.STARTED)

    result = user_session_repo.get_registered(user.id)

    assert result.exists() is False


def test_get_registered_skips_sessions_of_other_users(user_session_repo, user, other_user, game_session):
    UserSession.create(user=other_user, game_session=game_session)

    result = user_session_repo.get_registered(user.id)

    assert result.exists() is False


def test_get_registered_returns_empty_when_user_has_no_sessions(user_session_repo, user):
    result = user_session_repo.get_registered(user.id)

    assert result.exists() is False


def test_get_registered_returns_only_registered_session_for_specified_user(
        user_session_repo, user, other_user, game_session, other_game_session,
):
    UserSession.create(user=user, game_session=game_session)
    UserSession.create(user=user, game_session=other_game_session, state=SessionState.STARTED)
    UserSession.create(user=other_user, game_session=game_session)

    result = user_session_repo.get_registered(user.id)

    assert result.count() == 1
    assert result.first().state == SessionState.REGISTERED
    assert result.first().user.id == user.id


@pytest.mark.parametrize("non_finished_state", [
    SessionState.REGISTERED,
    SessionState.STARTED,
])
def test_has_non_finished_returns_true_for_any_non_finished_state(user_session_repo, user_session, non_finished_state):
    user_session.state = non_finished_state
    user_session.save()

    assert user_session_repo.has_non_finished(user_session.game_session.id) is True


def test_has_non_finished_returns_false_when_all_sessions_are_finished(user_session_repo, user_session):
    user_session.state = SessionState.FINISHED
    user_session.save()

    assert user_session_repo.has_non_finished(user_session.game_session.id) is False


def test_has_non_finished_returns_false_when_no_sessions_exist(user_session_repo, game_session):
    assert user_session_repo.has_non_finished(game_session.id) is False


def test_has_non_finished_ignores_sessions_of_other_game_session(
        user_session_repo, user, user_session, other_game_session
):
    user_session.state = SessionState.FINISHED
    user_session.save()
    UserSession.create(user=user, game_session=other_game_session)

    assert user_session_repo.has_non_finished(user_session.game_session.id) is False
