from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from collections.abc import Iterable
from core.dto.keyboard_item import KeyboardItem
from core.enums.callback_types import CallBackType
from core.dto.city_item import CityEnum


def commands_for_player() -> InlineKeyboardMarkup:
    """
    Клавиатура с доступными командами для игрока.
    """
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(
            text=" Записаться на игру ",
            callback_data=CallBackType.REGISTRATION
        ),
        InlineKeyboardButton(
            text=" Отменить запись ",
            callback_data=CallBackType.CANCEL
        ),
        InlineKeyboardButton(
            text=" Информация о записях ",
            callback_data=CallBackType.INFO
        ),
        InlineKeyboardButton(
            text=" Написать в поддержку ",
            callback_data=CallBackType.HELP
        ),
    )
    return markup


def commands_for_admin() -> InlineKeyboardMarkup:
    """
    Клавиатура с доступными командами для администратора.
    """
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(
            text=" Создать игру ",
            callback_data=CallBackType.CREATE_SESSION
        ),
        InlineKeyboardButton(
            text=" Начать / Отменить игру ",
            callback_data=CallBackType.MANAGE_SESSION
        ),
    )
    return markup


def review_keyboard(point_progress_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для проверки ответа игрока.

    Кнопки:
    -------
    - "Правильно" (callback_data="{CallBackType.ANSWER_CORRECT}:{point_progress_id}")
    - "Неправильно" (callback_data="{CallBackType.ANSWER_WRONG}:{point_progress_id}")
    :param point_progress_id: PointProgress.id
    """
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text="\u2705 Правильно",
            callback_data=f"{CallBackType.ANSWER_CORRECT}:{point_progress_id}"
        ),
        InlineKeyboardButton(
            text="\u274C Неправильно",
            callback_data=f"{CallBackType.ANSWER_WRONG}:{point_progress_id}"
        )
    )
    return markup


def cancel_or_back_keyboard(prev_func: bool = True) -> InlineKeyboardMarkup:
    """
    Клавиатура для отмены действия или перехода к предыдущему состоянию.

    :param prev_func: отражает наличие предыдущей функции(по умолчанию True).
    Если False: не добавляется кнопка "Назад"

    Кнопки:
    -------
    - "❌ Отмена" (callback_data="{CallBackType.CANCEL_ACTION}")
    - "◀️ Назад" (callback_data="{CallBackType.BACK}")
    """
    markup = InlineKeyboardMarkup()
    if prev_func:
        markup.add(
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data=f"{CallBackType.CANCEL_ACTION}"
            ),
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data=f"{CallBackType.BACK}"
            )
        )
    else:
        markup.add(
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data=f"{CallBackType.CANCEL_ACTION}"
            )
        )
    return markup


def city_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора города проведения игры.

    Кнопки:
    -------
    - "Название города" (callback_data="{CallBackType.CITY_CHOICE}{название города}")
    """
    markup = InlineKeyboardMarkup()

    for city in CityEnum:
        markup.add(
            InlineKeyboardButton(
                text=city.value.title,
                callback_data=f"{CallBackType.CITY_CHOICE}:{city.value.key}"
            )
        )
    return markup


def objects_keyboard(
        objects: Iterable[KeyboardItem],
        callback_data: str,
        row_width: int = 1
) -> InlineKeyboardMarkup:

    markup = InlineKeyboardMarkup(row_width=row_width)

    for obj in objects:
        markup.add(InlineKeyboardButton(
            text=obj.label,
            callback_data=f"{callback_data}:{obj.id}"))
    return markup


def get_clue_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для получения подсказки
    Кнопки:
    -------
    "Нужна подсказка" (callback_data=f"{CallBackType.GET_CLUE})
    """
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text="Нужна подсказка",
            callback_data=f"{CallBackType.GET_CLUE}"
        )
    )


def combine_keyboards(*keyboards: InlineKeyboardMarkup) -> InlineKeyboardMarkup:
    combined = InlineKeyboardMarkup()
    for kb in keyboards:
        for row in kb.keyboard:
            combined.keyboard.append(row)
    return combined


def start_or_delete_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора действия

    Кнопки:
    -------
    - "Начать игру" (callback_data="{CallBackType.START_SESSION}")
    - "Удалить игру" (callback_data="{CallBackType.DELETE_SESSION}")
    """
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text="Начать игру",
            callback_data=CallBackType.START_SESSION
        ),
        InlineKeyboardButton(
            text="Удалить игру",
            callback_data=CallBackType.DELETE_SESSION
        )
    )
    return markup


def confirm_create_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для подтверждения создания игровой сессии.
    -------
    - "Создать игру" (callback_data=CallBackType.CREATE_SESSION)
    """
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text="Создать игру",
            callback_data=CallBackType.CREATE_CONFIRM
        )
    )


def arrived_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура прибытия на локацию.

    Кнопки:
    -------
    - "Я на месте 🎉" (callback_data=CallBackType.ARRIVED)
    """
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text="Я на месте 🎉",
            callback_data=CallBackType.ARRIVED
        )
    )
