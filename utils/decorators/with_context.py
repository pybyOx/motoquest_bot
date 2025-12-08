from functools import wraps
import logging
from peewee import DoesNotExist
from repositories.repositories import (PlayerRepository, UserPointProgressRepository)
from telebot.types import Message, CallbackQuery


def with_context(include_player=False, include_player_session=False, include_user_point_progress=False):
    """Декоратор, извлекающий из message или callback:

    Общие данные:
    ------------
    - user_id : int
    - username : str
    - chat_id : int
    - data: str | list[PhotoSize] | None
    - message_id: int
    - content_type: str | None

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
        def wrapper(*args, **kwargs):
            if not kwargs:  # значит вызов первичный и нужно определять kwargs
                if args:
                    message_or_callback: Message | CallbackQuery = args[0]
                    args = args[1:]
                else:
                    raise ValueError("message_or_callback is required")

                user_id = message_or_callback.from_user.id
                username = message_or_callback.from_user.full_name

                if isinstance(message_or_callback, Message):
                    message = message_or_callback
                    message_id = message.message_id
                    chat_id = message.chat.id
                    content_type = message.content_type
                    if content_type == "text":
                        data = message.text
                    elif content_type == "photo":
                        data = message.photo
                    else:
                        data = None

                elif isinstance(message_or_callback, CallbackQuery):
                    call = message_or_callback
                    message_id = call.message.message_id
                    chat_id = call.message.chat.id
                    content_type = None
                    data = call.data
                else:
                    raise ValueError("Неверный тип message_or_callback")

                kwargs.update(user_id=user_id, username=username, chat_id=chat_id, message_id=message_id, data=data,
                              content_type=content_type)

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
