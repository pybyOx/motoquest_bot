from dataclasses import dataclass


@dataclass(frozen=True)
class KeyboardItem:
    id: int  # id в {cb: <id>}
    label: str  # текст кнопки
