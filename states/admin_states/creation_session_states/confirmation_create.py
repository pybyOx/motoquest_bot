from __future__ import annotations
from core.enums.callback_types import CallBackType
from core.exceptions import AlreadyExistsError
from keyboards import combine_keyboards, cancel_or_back_keyboard, confirm_create_keyboard
from states.base_state import BaseUserState
from presenters.telegram.creation_info_presenter import build_session_info_text
from typing import TYPE_CHECKING, Callable, Any

if TYPE_CHECKING:
    from core.dto.context import Context
    from database.models.admin_draft import AdminDraft
    from database.models.user import User


class CreateConfirmationState(BaseUserState):

    def __init__(self, services):
        super().__init__(services)
        self._callback_handlers = {
            CallBackType.CANCEL_ACTION: self.handle_cancel_action,
            CallBackType.BACK: self.handle_back,
            CallBackType.CREATE_CONFIRM: self.handle_create_game_session,
        }

    def render(self, user_id: int, notify_text: str | None = None) -> None:
        user: User = self._user.get_by_id(model_id=user_id)
        draft: AdminDraft = self._draft.get_by_id(user_id)
        session_info: str = build_session_info_text(
            game_title=draft.game_info.title,
            city_title=draft.city,
            location=draft.location,
            date_utc=draft.date,
            timezone=draft.timezone
        )

        text = (f"{session_info}\n"
                f"Если данные верны, подтвердите создание игры:")
        if notify_text:
            text = f"{notify_text}\n\n{text}"

        self._ui.show_user_ui(
            user=user,
            text=text,
            keyboard=combine_keyboards(
                confirm_create_keyboard(),
                cancel_or_back_keyboard()
            ),
            parse_mode="HTML",
            disable_web_page_preview=True
        )

    def handle_create_game_session(self, ctx: Context, **_: Any) -> None:
        creation_draft: AdminDraft = self._draft.get_by_id(ctx.user_id)
        try:
            self._game_session.create(dict(
                game_info=creation_draft.game_info,
                city=creation_draft.city,
                timezone=creation_draft.timezone,
                location=creation_draft.location,
                date=creation_draft.date
            ))
        except AlreadyExistsError:
            text = "⚠️ GameSession с такими данными уже существует."
        else:
            text = "✅ Игра успешно создана."
        self._finish_admin_action(ctx.user_id, text)

    def _handle_message(self, ctx: Context, **_: Any) -> None:
        self.render(ctx.user_id, "Нажмите кнопку для подтверждения.")

    @property
    def callback_handlers(self) -> dict[str, Callable[..., None]]:
        return self._callback_handlers
