from __future__ import annotations
from core.dto.keyboard_item import KeyboardItem
from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.point_progress import PointProgress


def build_keyboard_items(objects: Iterable) -> list[KeyboardItem]:
    return [KeyboardItem(id=obj.id, label=f"{obj}") for obj in objects]


def build_point_progresses_keyboard_items(
        progresses: Iterable[PointProgress]
) -> list[KeyboardItem]:
    return [
        KeyboardItem(id=progress.point.id, label=progress.point.title)
        for progress in progresses
    ]
