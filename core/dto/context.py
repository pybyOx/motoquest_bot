from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from database.models.user import User
    from core.enums.user_states import UserState
    from states.base_state import BaseUserState


@dataclass(frozen=True)
class Context:
    user: User
    full_name: str
    username: str | None
    user_id: int
    user_state: UserState
    state_obj: BaseUserState
    chat_id: int
    message_id: int
    callback_id: int | None
    content_type: str
    data: Any
