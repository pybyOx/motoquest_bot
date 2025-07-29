from functools import wraps
import logging
from peewee import DoesNotExist
from repositories.repositories import (PlayerRepository, UserPointProgressRepository)


def with_context(include_player=False, include_player_session=False, include_user_point_progress=False):
    """Декоратор, извлекающий из message или callback:

    Общие данные:
    ------------
    - user_id : int
    - username : str
    - chat_id : int
    - message_or_callback: Message | Callback
    - message_id: int

    include_player = True:
    -------------
    - player : Player

    include_player_session = True:
    -------------
    - player_session : PlayerSession (текущая сессия игрока со статусом started)
    - current_point : Point

    include_user_point_progress = True:
    -------------
    - user_point_progress : UserPointProgress (прогресс по точке)
    - clues_left : int (количество оставшихся подсказок)"""

    if include_user_point_progress:
        include_player = True
        include_player_session = True
    elif include_player_session:
        include_player = True

    def decorator(handler):
        @wraps(handler)
        def wrapper(message_or_callback, *args, **kwargs):
            user_id = message_or_callback.from_user.id
            username = message_or_callback.from_user.full_name
            if hasattr(message_or_callback, 'chat'):
                chat_id = message_or_callback.chat.id
            else:
                chat_id = message_or_callback.message.chat.id
            if hasattr(message_or_callback, 'message'):
                message_id = message_or_callback.message.message_id
            else:
                message_id = message_or_callback.message_id
            kwargs.update(user_id=user_id, username=username, chat_id=chat_id,
                          message_or_callback=message_or_callback, message_id=message_id)

            if include_player:
                try:
                    player = PlayerRepository.get(user_id=user_id)
                except DoesNotExist:
                    player = PlayerRepository.create(user_id=user_id, username=username)
                kwargs.update(player=player)

                if include_player_session:
                    player_session = player.current_player_session
                    if not player_session:
                        raise ValueError(f"{player}: отсутствует current_player_session")

                    current_point = player_session.current_point
                    if not current_point:
                        raise ValueError(f"{player_session}: отсутствует current_point")

                    kwargs.update(player_session=player_session, current_point=current_point)

                    if include_user_point_progress:
                        try:
                            user_point_progress = UserPointProgressRepository.get(player_session=player_session,
                                                                                  point=current_point)
                        except DoesNotExist as error:
                            logging.error(f" При получении UserPointProgress: {error}", exc_info=True)
                            raise

                        clues_left = 3 - user_point_progress.clues_used
                        kwargs.update(user_point_progress=user_point_progress, clues_left=clues_left)
            return handler(*args, **kwargs)
        return wrapper
    return decorator
