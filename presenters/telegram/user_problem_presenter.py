def build_problem_text(
        problem_msg: str,
        user_id: int,
        username: str | None,
        full_name: str,
) -> str:
    user_info = (
        f"@{username}"
        if username
        else f'<a href="tg://user?id={user_id}">{full_name}</a>'
    )

    return (
        f'Пользователю {user_info} нужна помощь:\n'
        f"{problem_msg}"
    )
