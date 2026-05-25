from peewee import DoesNotExist
from core.exceptions import AlreadyExistsError
from database.models.user import User
import pytest


def test_get_by_id_returns_user(user_repo, existing_user):
    user = user_repo.get_by_id(existing_user.id)

    assert user == existing_user


def test_get_by_id_raises_does_not_exist_for_unknown_id(user_repo, existing_user):
    with pytest.raises(DoesNotExist):
        user_repo.get_by_id(999)


def test_get_or_none_returns_user_if_exists(user_repo, existing_user):
    user = user_repo.get_or_none(id=existing_user.id)

    assert user == existing_user


def test_get_or_none_returns_none_if_not_exists(user_repo, existing_user):
    result = user_repo.get_or_none(id=999)

    assert result is None


def test_create_returns_user(user_repo):
    user = user_repo.create(
        dict(
            id=123,
            username="user_123"
        )
    )

    assert isinstance(user, User)
    assert user.id == 123
    assert user.username == "user_123"


def test_create_raises_already_exists_error_on_duplicate_id(user_repo):
    user_repo.create(dict(id=123))

    with pytest.raises(AlreadyExistsError) as exc_info:
        user_repo.create(dict(id=123))

    assert "id" in str(exc_info.value)


def test_delete_by_id_removes_user(user_repo, existing_user):
    updated_count = user_repo.delete_by_id(existing_user.id)

    result = user_repo.get_or_none(id=existing_user.id)

    assert result is None
    assert updated_count == 1


def test_delete_by_id_raises_does_not_exist_for_unknown_id(user_repo, existing_user):
    with pytest.raises(DoesNotExist):
        user_repo.delete_by_id(999)
