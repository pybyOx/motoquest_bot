from __future__ import annotations
from core.enums.callback_types import CallBackType
from core.enums.user_states import UserState
from database.db import db
from keyboards import cancel_or_back_keyboard
from states.base_state import BaseUserState
from core.utils.check_data import parse_user_datetime_to_utc
from typing import TYPE_CHECKING, Callable, Any

if TYPE_CHECKING:
    from database.models.user import User
    from core.dto.context import Context


class DateChoiceState(BaseUserState):

    def __init__(self, services):
        super().__init__(services)
        self._callback_handlers = {
            CallBackType.CANCEL_ACTION: self.handle_cancel_action,
            CallBackType.BACK: self.handle_back,
        }

    def render(self, user_id: int, notify_text: str | None = None) -> None:
        user: User = self._user.get_by_id(model_id=user_id)
        text = "Введите дату и время начала (в формате ДД.ММ.ГГГГ ЧЧ:ММ):"
        if notify_text:
            text = f"{notify_text}\n\n{text}"

        self._ui.show_user_ui(
            user=user,
            text=text,
            keyboard=cancel_or_back_keyboard(),
        )

    def _handle_message(self, ctx: Context, **_: Any) -> None:
        user_timezone = self._draft.get_by_id(ctx.user_id).timezone
        try:
            date_utc = parse_user_datetime_to_utc(
                date_str=ctx.data,
                user_timezone=user_timezone
            )
        except ValueError:
            self.render(ctx.user_id, "Неверный формат. Попробуйте ещё раз: ДД.ММ.ГГГГ ЧЧ:ММ")
        else:

            with db.atomic():
                self._draft.update_by_id(ctx.user_id, date=date_utc)
                self._state.transition(ctx.user_id, UserState.confirmation)
            self._state.render(ctx.user_id, UserState.confirmation)

    @property
    def callback_handlers(self) -> dict[str, Callable[..., None]]:
        return self._callback_handlers
