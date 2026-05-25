

def test_get_active_from_only_active(game_session_repo, game_session):
    result = game_session_repo.get_active()

    assert result.count() == 1
    assert result.first().id == game_session.id


def test_get_active_from_active_and_finished(game_session_repo, game_session, finished_game_session):
    result = game_session_repo.get_active()

    assert result.count() == 1
    assert result.first().id == game_session.id


def test_get_active_from_finished(game_session_repo, finished_game_session):
    result = game_session_repo.get_active()

    assert result.exists() is False


def test_get_active_from_empty(game_session_repo):
    result = game_session_repo.get_active()

    assert result.exists() is False


def test_set_finished_updates_field(game_session_repo, game_session):
    updated_count = game_session_repo.set_finished(game_session.id)

    game_session_from_db = game_session_repo.get_by_id(game_session.id)
    assert updated_count == 1
    assert game_session_from_db.finished is True


def test_set_finished_does_not_affect_other_session(game_session_repo, game_session, other_game_session):
    game_session_repo.set_finished(game_session.id)

    other_session_from_db = game_session_repo.get_by_id(other_game_session.id)
    assert other_session_from_db.finished is False


def test_set_finished_returns_zero_if_session_not_found(game_session_repo):
    updated_count = game_session_repo.set_finished(999)

    assert updated_count == 0
