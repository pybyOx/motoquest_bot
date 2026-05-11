from __future__ import annotations
from core.enums.callback_types import CallBackType
from core.enums.user_states import UserState
from database.db import db
from keyboards import cancel_or_back_keyboard
from states.base_state import BaseUserState
from typing import TYPE_CHECKING, Callable, Any
from core.utils.check_data import is_url_accessible

if TYPE_CHECKING:
    from core.dto.context import Context
    from database.models.user import User


class LocationChoiceState(BaseUserState):

    def __init__(self, services):
        super().__init__(services)
        self._callback_handlers = {
            CallBackType.CANCEL_ACTION: self.handle_cancel_action,
            CallBackType.BACK: self.handle_back,
        }

    def render(self, user_id: int, notify_text: str | None = None) -> None:
        user: User = self._user.get_by_id(model_id=user_id)
        text = "Пришлите ссылку на место встречи"
        if notify_text:
            text = f"{notify_text}\n\n{text}"

        self._ui.show_user_ui(
            user=user,
            text=text,
            keyboard=cancel_or_back_keyboard(),
        )

    def _handle_message(self, ctx: Context, **_: Any) -> None:
        data = ctx.data.strip()
        if is_url_accessible(url=data):

            with db.atomic():
                self._draft.update_by_id(ctx.user_id, location=data)
                self._state.transition(ctx.user_id, UserState.choice_date)
            self._state.render(ctx.user_id, UserState.choice_date)
        else:
            self.render(ctx.user_id, "Некорректная ссылка.")

    @property
    def callback_handlers(self) -> dict[str, Callable[..., None]]:
        return self._callback_handlers
