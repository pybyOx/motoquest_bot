from database.models.user_event import UserEvent
from database.repositories.base_repository import BaseRepository
from core.enums.user_event_types import UserEventType
from peewee import IntegrityError


class UserEventRepository(BaseRepository[UserEvent]):
    def __init__(self):
        super().__init__(UserEvent)

    def create_once(self, user_session_id: int, event_type: UserEventType) -> bool:
        """
        Фиксирует отправку сообщения, если оно ещё не отправлялось.

        :return: True — если сообщение нужно отправить
                 False — если уже было отправлено
        """
        try:
            self.model.create(user_session=user_session_id, event_type=event_type)
            return True
        except IntegrityError:
            return False
