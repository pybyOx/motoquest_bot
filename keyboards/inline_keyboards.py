from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from peewee import ModelSelect
from database.database_model import GameInfo, GameSession, PlayerSession, UserPointProgress


def start_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура с доступными командами:

    Кнопки:
    -------
    - /register - Записаться на игру (callback_data="register")
    - /cancel - Отменить запись (callback_data="cancel")
    - /info - Информация о записях и пройденных играх  (callback_data="info")
    - /help - Написать в поддержку (callback_data="help")
    """
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(" /register - Записаться на игру ", callback_data="register"),
        InlineKeyboardButton(" /cancel - Отменить запись ", callback_data="cancel"),
        InlineKeyboardButton(" /info - Информация о записях и пройденных играх ", callback_data="info"),
        InlineKeyboardButton(" /help - Написать в поддержку ", callback_data="help")
    )
    return markup


def review_keyboard(user_point_progress_id) -> InlineKeyboardMarkup:
    """
    Клавиатура для проверки ответа игрока.

    Кнопки:
    -------
    - "Правильно" (callback_data="answer_correct:{user_point_progress_id}")
    - "Неправильно" (callback_data="answer_wrong:{user_point_progress_id}")
    :param user_point_progress_id: ID UserPointProgress.
    """
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("\u2705 Правильно", callback_data=f"answer_correct:{user_point_progress_id}"),
        InlineKeyboardButton("\u274C Неправильно", callback_data=f"answer_wrong:{user_point_progress_id}")
    )
    return markup


def start_or_delete_keyboard(session_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для управления игровой сессией.

    Кнопки:
    -------
    - "Начать игру" (callback_data="start_game:{session_id}")
    - "Удалить игру" (callback_data="delete_game:{session_id}")
    :param session_id: ID GameSession.
    """
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Начать игру", callback_data=f"start_game:{session_id}"),
        InlineKeyboardButton("Удалить игру", callback_data=f"delete_game:{session_id}")
    )
    return markup


def confirm_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для подтверждения действия.

    Кнопки:
    -------
    - "✅ Да" (callback_data="confirm_yes")
    - "❌ Нет" (callback_data="confirm_no")
    """
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Да", callback_data="confirm_yes"),
               InlineKeyboardButton("❌ Нет", callback_data="confirm_no"))
    return markup


def cancel_or_back_keyboard(prev_func: bool = True) -> InlineKeyboardMarkup:
    """
    Клавиатура для отмены действия или перехода к предыдущему состоянию.

    :param prev_func: отражает наличие предыдущей функции(по умолчанию True). Если False: не добавляется кнопка "Назад"

    Кнопки:
    -------
    - "❌ Отмена" (callback_data="cancel_action")
    - "◀️ Назад" (callback_data="back")
    """
    markup = InlineKeyboardMarkup()
    if prev_func:
        markup.add(
            InlineKeyboardButton("❌ Отмена", callback_data="cancel_action"),
            InlineKeyboardButton("◀️ Назад", callback_data="back")
        )
    else:
        markup.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel_action"))
    return markup


def city_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора города проведения игры.

    Кнопки:
    -------
    - "Название города" (callback_data="city:{название города}")
    """
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Нячанг", callback_data="city:nha_trang"),
               InlineKeyboardButton("Ханой", callback_data="city:hanoi"))
    return markup


def objects_keyboard(objects: ModelSelect, callback_data: str, row_width: int = 1) -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора объекта из выборки.

    :param objects: Выборка объектов классов GameSession / GameInfo / PlayerSession/ UserPointProgress.
    :param callback_data: "register:" / "manage_game:" / "create_game:" / "cancel:" / "select_point:"
    :param row_width: Количество кнопок в одной строке клавиатуры(по умолчанию 1)
    :raises ValueError: Неверно передан callback_data.
    :raises TypeError: Объекты выборки games не являются объектами классов
    GameSession / GameInfo / PlayerSession / UserPointProgress.
    """
    if callback_data not in ("register:", "manage_game:", "create_game:", "cancel:", "select_point:"):
        raise ValueError(f'Аргумент callback_data должен соответствовать одному из значений: '
                         f'"register:", "manage_game:", "create_game:", "cancel:", "select_point:"')

    markup = InlineKeyboardMarkup(row_width=row_width)

    for obj in objects:
        if isinstance(obj, GameInfo):
            obj_id = obj.game_id
            text = f"{obj}"
        elif isinstance(obj, GameSession):
            obj_id = obj.session_id
            text = f"{obj}"
        elif isinstance(obj, PlayerSession):
            obj_id = obj.player_session_id
            text = f"{obj.game_session}"
        elif isinstance(obj, UserPointProgress):
            obj_id = obj.point.point_id
            text = f"{obj.point.title}"
        else:
            raise TypeError("Переданная выборка objects должна содержать объекты классов "
                            "GameSession / GameInfo / PlayerSession / UserPointProgress.")

        markup.add(InlineKeyboardButton(text=text, callback_data=f"{callback_data}{obj_id}"))
    return markup


def clue_keyboard(clues_left: int):
    markup = InlineKeyboardMarkup(row_width=2)

    if clues_left > 0:
        markup.add(InlineKeyboardButton(text=f"Нужна подсказка\n(осталось: {clues_left})", callback_data="get_clue"))

    return markup


def combine_keyboards(*keyboards: InlineKeyboardMarkup) -> InlineKeyboardMarkup:
    combined = InlineKeyboardMarkup()
    for kb in keyboards:
        for row in kb.keyboard:
            combined.keyboard.append(row)
    return combined
