from database.models.user_event import UserEvent
from database.repositories.base_repository import BaseRepository
from core.enums.user_event_types import UserEventType


class UserEventRepository(BaseRepository[UserEvent]):
    def __init__(self):
        super().__init__(UserEvent)

    def create_once(self, user_session_id: int, event_type: UserEventType) -> bool:
        """
        Фиксирует отправку сообщения, если оно ещё не отправлялось.

        :return: True — если сообщение нужно отправить
                 False — если уже было отправлено
        """
        created = self.model.insert(
            user_session=user_session_id,
            event_type=event_type
        ).on_conflict_ignore().execute()

        return created == 1
