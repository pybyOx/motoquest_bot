from core.container import get_container
from core.enums.user_role_types import RoleType
from core.utils.check_data import get_data_from_argv

container = get_container()
user_repo = container.user_repo


def set_admin(tg_id: int):
    user, _ = user_repo.get_or_create_by_id(tg_id)
    user_repo.update_role(user_id=tg_id, role=RoleType.ADMIN)
    print(f"User {user.id} is now admin")


if __name__ == "__main__":  # python -m cli.set_admin 395578226
    user_id: int = int(get_data_from_argv(length=2, index=1))
    set_admin(user_id)
