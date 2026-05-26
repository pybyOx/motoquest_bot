import pytest
from peewee import DoesNotExist

from core.exceptions import AlreadyExistsError
from database.models.user import User


# ── get_by_id ─────────────────────────────────────────────────────────────────

def test_get_by_id_returns_user(user_repo, user):
    user_from_db = user_repo.get_by_id(user.id)

    assert user_from_db == user


def test_get_by_id_raises_does_not_exist_for_unknown_id(user_repo, user):
    with pytest.raises(DoesNotExist):
        user_repo.get_by_id(999)


# ── create ────────────────────────────────────────────────────────────────────

def test_create_returns_user(user_repo):
    user = user_repo.create({"id": 123, "username": "user_123"})

    assert isinstance(user, User)
    assert user.id == 123
    assert user.username == "user_123"


def test_create_raises_already_exists_error_on_duplicate_id(user_repo):
    user_repo.create({"id": 123})

    with pytest.raises(AlreadyExistsError) as exc_info:
        user_repo.create({"id": 123})

    assert "id" in str(exc_info.value)


# ── delete_by_id ──────────────────────────────────────────────────────────────

def test_delete_by_id_removes_user(user_repo, user):
    updated_count = user_repo.delete_by_id(user.id)

    assert updated_count == 1
    with pytest.raises(DoesNotExist):
        user_repo.get_by_id(user.id)


def test_delete_by_id_raises_does_not_exist_for_unknown_id(user_repo, user):
    with pytest.raises(DoesNotExist):
        user_repo.delete_by_id(999)
