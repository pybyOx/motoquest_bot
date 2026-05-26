from datetime import datetime

from database.models.admin_draft import AdminDraft


def test_reset_all_clears_all_fields(admin_draft_repo, game_info, game_session):
    draft = AdminDraft.create(
        user_id=123,
        game_info=game_info,
        city="Москва",
        timezone="Europe/Moscow",
        location="Парк Горького",
        date=datetime(2026, 6, 1, 12, 0),
        game_session=game_session,
    )

    updated_count = admin_draft_repo.reset_all(draft.user_id)

    draft_from_db = admin_draft_repo.get_by_id(draft.user_id)
    assert updated_count == 1
    assert draft_from_db.game_info is None
    assert draft_from_db.city is None
    assert draft_from_db.timezone is None
    assert draft_from_db.location is None
    assert draft_from_db.date is None
    assert draft_from_db.game_session is None


def test_reset_all_does_not_affect_other_drafts(admin_draft_repo):
    draft = AdminDraft.create(user_id=123, city="Москва")
    other_draft = AdminDraft.create(user_id=456, city="Питер")

    admin_draft_repo.reset_all(draft.user_id)

    other_from_db = admin_draft_repo.get_by_id(other_draft.user_id)
    assert other_from_db.city == "Питер"


def test_reset_all_returns_zero_if_user_not_found(admin_draft_repo):
    updated_count = admin_draft_repo.reset_all(999)

    assert updated_count == 0
