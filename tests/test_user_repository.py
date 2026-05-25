from core.enums.user_role_types import RoleType
from core.enums.user_states import UserState
import pytest

UPDATE_METHODS = [
    ("update_role", "role", RoleType.ADMIN, RoleType.PLAYER),
    ("update_state", "state", UserState.registration, UserState.idle),
]


def test_get_or_create_by_id_creates_new_user(user_repo):
    user, created = user_repo.get_or_create_by_id(user_id=123, username="oksana")

    assert created is True
    assert user.id == 123
    assert user.username == "oksana"
    assert user.role == RoleType.PLAYER
    assert user.state == UserState.idle
    assert user.recovery_attempts == 0
    assert user.is_error is False


def test_get_or_create_by_id_returns_existing_user(user_repo):
    user_repo.get_or_create_by_id(user_id=123, username="oksana")

    user, created = user_repo.get_or_create_by_id(user_id=123, username="oksana")

    assert created is False
    assert user.id == 123
    assert user.username == "oksana"


def test_get_or_create_by_id_updates_username_if_changed(user_repo):
    user_repo.get_or_create_by_id(user_id=123, username="oksana")

    user, created = user_repo.get_or_create_by_id(user_id=123, username="oksana_2")
    user_from_db = user_repo.get_by_id(model_id=123)

    assert created is False
    assert user.id == 123
    assert user_from_db.id == 123
    assert user.username == "oksana_2"
    assert user_from_db.username == "oksana_2"


def test_get_or_create_by_id_does_not_overwrite_username_with_none(user_repo):
    user_repo.get_or_create_by_id(user_id=123, username="oksana")

    user, created = user_repo.get_or_create_by_id(user_id=123, username=None)

    assert created is False
    assert user.id == 123
    assert user.username == "oksana"


def test_get_or_create_by_id_works_without_username(user_repo):
    user, created = user_repo.get_or_create_by_id(user_id=123)

    assert created is True
    assert user.id == 123
    assert user.username is None


@pytest.mark.parametrize("method_name,field_name,new_value,default_value", UPDATE_METHODS)
def test_update_method_changes_field(
        user_repo, existing_user,
        method_name, field_name, new_value, default_value,
):
    method = getattr(user_repo, method_name)
    updated_count = method(existing_user.id, new_value)
    user_from_db = user_repo.get_by_id(existing_user.id)

    assert updated_count == 1
    assert getattr(user_from_db, field_name) == new_value


@pytest.mark.parametrize("method_name,field_name,new_value,default_value", UPDATE_METHODS)
def test_update_method_does_not_affect_other_users(
        user_repo, existing_user,
        method_name, field_name, new_value, default_value,
):
    method = getattr(user_repo, method_name)
    other_user, _ = user_repo.get_or_create_by_id(user_id=456)

    method(existing_user.id, new_value)

    other_user_from_db = user_repo.get_by_id(other_user.id)

    assert getattr(other_user_from_db, field_name) == default_value


@pytest.mark.parametrize("method_name,field_name,new_value,default_value", UPDATE_METHODS)
def test_update_method_returns_zero_if_user_not_found(
        user_repo, existing_user,
        method_name, field_name, new_value, default_value,
):
    method = getattr(user_repo, method_name)
    updated_count = method(999, new_value)

    assert updated_count == 0


def test_increment_recovery_attempts_increases_by_one(user_repo, existing_user):
    updated_count = user_repo.increment_recovery_attempts(existing_user.id)

    user_from_db = user_repo.get_by_id(existing_user.id)
    assert existing_user.recovery_attempts == 0
    assert user_from_db.recovery_attempts == 1
    assert updated_count == 1


def test_increment_recovery_attempts_accumulates(user_repo, existing_user):
    for _ in range(3):
        user_repo.increment_recovery_attempts(existing_user.id)

    user_from_db = user_repo.get_by_id(existing_user.id)
    assert user_from_db.recovery_attempts == 3


def test_increment_recovery_attempts_does_not_affect_other_users(user_repo, existing_user):
    other_user, _ = user_repo.get_or_create_by_id(user_id=456)

    user_repo.increment_recovery_attempts(existing_user.id)

    other_user_from_db = user_repo.get_by_id(other_user.id)
    assert other_user_from_db.recovery_attempts == 0


def test_increment_recovery_attempts_returns_zero_if_user_not_found(user_repo, existing_user):
    updated_count = user_repo.increment_recovery_attempts(999)
    assert updated_count == 0


def test_reset_recovery_attempts_sets_to_zero(user_repo, existing_user):
    existing_user.recovery_attempts = 3
    existing_user.save()

    user_repo.reset_recovery_attempts(existing_user.id)

    user_from_db = user_repo.get_by_id(existing_user.id)
    assert user_from_db.recovery_attempts == 0


def test_reset_recovery_attempts_does_not_affect_other_users(user_repo, existing_user):
    other_user, _ = user_repo.get_or_create_by_id(user_id=456)
    other_user.recovery_attempts = 2
    other_user.save()
    existing_user.recovery_attempts = 1
    existing_user.save()

    user_repo.reset_recovery_attempts(existing_user.id)

    other_user_from_db = user_repo.get_by_id(other_user.id)
    assert other_user_from_db.recovery_attempts == 2


def test_reset_recovery_attempts_returns_zero_if_user_not_found(user_repo, existing_user):
    updated_count = user_repo.reset_recovery_attempts(999)

    assert updated_count == 0
