from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from telebot.types import PhotoSize, Document


def is_allowed_answer_content(
        content_type: str,
        answer: str | list[PhotoSize] | Document
):
    if correct_content_type(content_type=content_type):
        if content_type == "document":
            if answer.mime_type and answer.mime_type.startswith("image/"):
                return True
            return False
        return True
    return False


def correct_content_type(content_type: str) -> bool:
    if content_type in ("text", "photo", "document"):
        return True
    return False
