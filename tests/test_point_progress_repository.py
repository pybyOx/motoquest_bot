from datetime import datetime

from database.models.point import Point
from database.models.point_progress import PointProgress


def test_start_progress_sets_started_at(point_progress_repo, point_progress, existing_datetime):
    updated_count = point_progress_repo.start_progress(
        point_progress.id,
        existing_datetime
    )
    point_progress_from_db = point_progress_repo.get_by_id(point_progress.id)
    assert updated_count == 1
    assert datetime.fromisoformat(point_progress_from_db.started_at) == existing_datetime


def test_start_progress_sets_datetime_now_if_non_started_at(point_progress_repo, point_progress):
    updated_count = point_progress_repo.start_progress(point_progress.id)

    point_progress_from_db = point_progress_repo.get_by_id(point_progress.id)
    assert updated_count == 1
    assert isinstance(datetime.fromisoformat(point_progress_from_db.started_at), datetime)


def test_start_progress_does_not_affect_other_point_progresses(
        point_progress_repo, point_progress, other_point_progress,
):
    point_progress_repo.start_progress(point_progress.id)

    other_point_progress_from_db = point_progress_repo.get_by_id(other_point_progress.id)
    assert other_point_progress_from_db.started_at is None


def test_start_progress_returns_zero_if_point_progress_not_found(point_progress_repo):
    updated_count = point_progress_repo.start_progress(999)

    assert updated_count == 0


def test_finish_progress_sets_finished_at_and_is_finished(point_progress_repo, point_progress, existing_datetime):
    updated_count = point_progress_repo.finish_progress(
        point_progress.id,
        existing_datetime
    )
    point_progress_from_db = point_progress_repo.get_by_id(point_progress.id)

    assert updated_count == 1
    assert datetime.fromisoformat(point_progress_from_db.finished_at) == existing_datetime
    assert point_progress_from_db.is_finished is True


def test_finish_progress_sets_datetime_now_if_non_finished_at(point_progress_repo, point_progress):
    updated_count = point_progress_repo.finish_progress(
        point_progress.id,
    )
    point_progress_from_db = point_progress_repo.get_by_id(point_progress.id)

    assert updated_count == 1
    assert isinstance(datetime.fromisoformat(point_progress_from_db.finished_at), datetime)


def test_finish_progress_does_not_affect_other_point_progresses(
        point_progress_repo, point_progress, other_point_progress,
):
    point_progress_repo.finish_progress(point_progress.id)

    other_point_progress_from_db = point_progress_repo.get_by_id(other_point_progress.id)
    assert other_point_progress_from_db.finished_at is None
    assert other_point_progress_from_db.is_finished is False


def test_finish_progress_returns_zero_if_point_progress_not_found(point_progress_repo):
    updated_count = point_progress_repo.finish_progress(999)

    assert updated_count == 0


def test_get_current_by_session_returns_current_point_progress(point_progress_repo, point_progress):
    user_session, point = point_progress.user_session, point_progress.point
    user_session.current_point = point
    user_session.save()

    result = point_progress_repo.get_current_by_session(user_session)

    assert result == point_progress


def test_get_current_by_session_returns_none_if_session_without_current_point(point_progress_repo, user_session):
    assert point_progress_repo.get_current_by_session(user_session) is None


def test_get_current_by_session_returns_none_when_no_progress_for_session(point_progress_repo, other_user_session):
    assert point_progress_repo.get_current_by_session(other_user_session) is None


def test_increment_clues_used_increases_by_one(point_progress_repo, point_progress):
    clues_used = point_progress_repo.increment_clues_used(point_progress.id)

    point_progress_from_db = point_progress_repo.get_by_id(point_progress.id)
    assert point_progress.clues_used == 0
    assert point_progress_from_db.clues_used == 1
    assert clues_used == 1


def test_increment_clues_used_accumulates(point_progress_repo, point_progress):
    for _ in range(3):
        point_progress_repo.increment_clues_used(point_progress.id)

    point_progress_from_db = point_progress_repo.get_by_id(point_progress.id)
    assert point_progress_from_db.clues_used == 3


def test_increment_clues_used_does_not_affect_other_point_progresses(
        point_progress_repo, point_progress, other_point_progress
):
    point_progress_repo.increment_clues_used(point_progress.id)

    other_point_progress_from_db = point_progress_repo.get_by_id(other_point_progress.id)
    assert other_point_progress_from_db.clues_used == 0


def test_increment_clues_used_returns_none_if_point_progress_not_found(point_progress_repo, point_progress):
    assert point_progress_repo.increment_clues_used(999) is None


def test_increment_clues_used_returns_none_if_limit_reached(point_progress_repo, point_progress):
    point_progress.clues_used = 3
    point_progress.save()

    result = point_progress_repo.increment_clues_used(point_progress.id)

    point_progress_from_db = point_progress_repo.get_by_id(point_progress.id)
    assert result is None
    assert point_progress_from_db.clues_used == 3


# ── create_for_session ────────────────────────────────────────────────────────

def _make_point(game_info, title="Point") -> Point:
    return Point.create(
        title=title,
        location={"link": "https://maps.example.com"},
        task={"text": "Задание"},
        answer={"text": "ответ", "type": "text"},
        after_solved={"text": "Решено"},
        game_info=game_info,
    )


def test_create_for_session_creates_one_progress_per_point(
        point_progress_repo, user_session, game_info,
):
    p1 = _make_point(game_info, "P1")
    p2 = _make_point(game_info, "P2")
    p3 = _make_point(game_info, "P3")

    point_progress_repo.create_for_session(user_session.id, [p1.id, p2.id, p3.id])

    assert PointProgress.select().count() == 3


def test_create_for_session_links_progress_to_session_and_points(
        point_progress_repo, user_session, game_info,
):
    p1 = _make_point(game_info, "P1")
    p2 = _make_point(game_info, "P2")

    point_progress_repo.create_for_session(user_session.id, [p1.id, p2.id])

    progresses = list(PointProgress.select().order_by(PointProgress.point))
    assert [pr.user_session.id for pr in progresses] == [user_session.id, user_session.id]
    assert sorted(pr.point.id for pr in progresses) == sorted([p1.id, p2.id])


def test_create_for_session_creates_nothing_for_empty_list(point_progress_repo, user_session):
    point_progress_repo.create_for_session(user_session.id, [])

    assert PointProgress.select().count() == 0


# ── get_non_finished_by_session ───────────────────────────────────────────────

def test_get_non_finished_by_session_returns_only_non_finished(
        point_progress_repo, user_session,
):
    PointProgress.create(user_session=user_session, is_finished=False)
    PointProgress.create(user_session=user_session, is_finished=True)

    result = point_progress_repo.get_non_finished_by_session(user_session.id)

    assert result.count() == 1
    assert result.first().is_finished is False


def test_get_non_finished_by_session_skips_progresses_of_other_sessions(
        point_progress_repo, user_session, other_user_session,
):
    PointProgress.create(user_session=other_user_session, is_finished=False)

    result = point_progress_repo.get_non_finished_by_session(user_session.id)

    assert result.exists() is False


def test_get_non_finished_by_session_returns_empty_when_no_progresses(
        point_progress_repo, user_session,
):
    result = point_progress_repo.get_non_finished_by_session(user_session.id)

    assert result.exists() is False


# ── has_non_finished ──────────────────────────────────────────────────────────

def test_has_non_finished_returns_true_when_non_finished_exists(
        point_progress_repo, user_session,
):
    PointProgress.create(user_session=user_session, is_finished=False)

    assert point_progress_repo.has_non_finished(user_session.id) is True


def test_has_non_finished_returns_false_when_all_finished(
        point_progress_repo, user_session,
):
    PointProgress.create(user_session=user_session, is_finished=True)

    assert point_progress_repo.has_non_finished(user_session.id) is False


def test_has_non_finished_returns_false_when_no_progresses(
        point_progress_repo, user_session,
):
    assert point_progress_repo.has_non_finished(user_session.id) is False


def test_has_non_finished_ignores_progresses_of_other_sessions(
        point_progress_repo, user_session, other_user_session,
):
    PointProgress.create(user_session=other_user_session, is_finished=False)

    assert point_progress_repo.has_non_finished(user_session.id) is False
