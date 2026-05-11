from __future__ import annotations
from functools import wraps
from core.container import get_container
from core.dto.context import Context
from core.enums.user_states import UserState
from telebot.types import Message, CallbackQuery
from typing import Any, TYPE_CHECKING


if TYPE_CHECKING:
    from states.base_state import BaseUserState

container = get_container()
user_repo = container.user_repo
state_factory = container.state_factory


def with_context():
    """Декоратор, дополняющий kwargs контекстом сообщения Telegram  - ctx: Context.

    Добавляемые параметры в Context:
    ------------
    - message_id (int): идентификатор сообщения Telegram.
    - user_id (int): идентификатор пользователя Telegram.
    - chat_id (int): идентификатор чата Telegram.
    - username (str | None): username пользователя.
    - full_name (str): полное имя пользователя.
    - content_type (str): тип сообщения (message.content_type) или "callback".
    - data:
            * str — если content_type == 'text'
            * List[PhotoSize] — если content_type == 'photo'
            * Document — если content_type == 'document'
            * None — для всех остальных типов сообщений
    - user (User): Объект пользователя.
    - user_state (UserState): Строковое представление состояния пользователя (user.state)
    - state_obj (BaseState): Объект состояния пользователя - этап игры или ее отсутствие.
    - user_session (UserSession | None): Текущая игровая сессия игрока или None.
    - current_point (Point | None): Текущая локация или None.
    - point_progress (PointProgress | None): Прогресс по текущей локации или None.
    """

    def decorator(handler):
        @wraps(handler)
        def wrapper(*args, **kwargs):

            if not kwargs:  # значит вызов первичный и нужно определять kwargs
                if not args:
                    raise ValueError("message_or_callback is required")

                message_or_callback: Message | CallbackQuery = args[0]
                args = args[1:]

                transport_context: dict[str, Any] = extract_transport_context(message_or_callback)

                user, _ = user_repo.get_or_create_by_id(
                    user_id=transport_context["user_id"],
                    username=transport_context["username"],
                )
                user_state: UserState = UserState(user.state)
                state_obj: BaseUserState = state_factory.get(state=user_state)

                ctx = Context(
                    user=user,
                    user_state=user_state,
                    state_obj=state_obj,
                    **transport_context
                )
                kwargs.update(ctx=ctx)
            return handler(*args, **kwargs)
        return wrapper
    return decorator


def extract_transport_context(
        message_or_callback: Message | CallbackQuery
) -> dict[str, Any]:
    if isinstance(message_or_callback, Message):
        msg = message_or_callback
        chat_id = msg.chat.id
        message_id = msg.message_id
        user_id = msg.from_user.id
        full_name = msg.from_user.full_name
        username = msg.from_user.username
        content_type = msg.content_type
        if content_type == "text":
            data = msg.text
        elif content_type == "photo":
            data = msg.photo
        elif content_type == "document":
            data = msg.document
        else:
            data = None

        return dict(
            chat_id=chat_id,
            message_id=message_id,
            callback_id=None,
            user_id=user_id,
            full_name=full_name,
            username=username,
            content_type=content_type,
            data=data
        )

    if isinstance(message_or_callback, CallbackQuery):
        return dict(
            chat_id=message_or_callback.message.chat.id,
            message_id=message_or_callback.message.message_id,
            callback_id=message_or_callback.id,
            user_id=message_or_callback.from_user.id,
            username=message_or_callback.from_user.username,
            full_name=message_or_callback.from_user.full_name,
            content_type="callback",
            data=message_or_callback.data
        )

    raise ValueError("Unsupported telegram update type")
