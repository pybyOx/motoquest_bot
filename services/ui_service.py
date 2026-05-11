from __future__ import annotations
from telebot.apihelper import ApiTelegramException
from config_data.config import INSPECTOR_ID
from presenters.telegram.user_answer_presenter import build_answer_text
from presenters.telegram.user_problem_presenter import build_problem_text
from presenters.telegram.build_data_text import build_data_text
from keyboards import review_keyboard
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from telebot import TeleBot
    from database.models.point import Point
    from database.models.user import User
    from telebot.types import InlineKeyboardMarkup
    from database.repositories.base_repository import BaseRepository
    from database.repositories.user_repository import UserRepository
    from pathlib import Path


class UIService:
    def __init__(
            self,
            bot: TeleBot,
            user_repo: UserRepository,
    ):
        self.bot = bot
        self.user_repo = user_repo

    def send_msg(
            self,
            chat_id: int,
            text: str,
            reply_to_message_id: int | None = None,
            keyboard: InlineKeyboardMarkup | None = None,
            parse_mode: str | None = None,
            disable_web_page_preview: bool = False,
    ) -> int:
        return self.bot.send_message(
            chat_id,
            text,
            reply_to_message_id=reply_to_message_id,
            reply_markup=keyboard,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
        ).message_id

    def send_location(self, chat_id: int, location: str, msg_id: int | None = None) -> int:
        """
        Отправляет сообщение с локацией в чат
        :param chat_id: id чата
        :param location: Текст сообщения, содержащий локацию
        :param msg_id: id сообщения, которое будет отредактировано (по умолчанию None)
        :return: id сообщения
        """
        if msg_id:
            return self.bot.edit_message_text(location, chat_id, msg_id,
                                              parse_mode="HTML",
                                              disable_web_page_preview=True
                                              ).message_id
        return self.bot.send_message(chat_id, location,
                                     parse_mode="HTML",
                                     disable_web_page_preview=True
                                     ).message_id

    def send_photo(self, chat_id: int, text: str, image_path: str) -> int:
        """
        Отправляет сообщение с изображением в чат
        :param chat_id: id чата
        :param text: Текст к изображению
        :param image_path: Путь к изображению
        :return: id сообщения
        """
        with open(image_path, "rb") as file:
            return self.bot.send_photo(
                chat_id=chat_id,
                photo=file,
                caption=text,
                parse_mode="HTML"
            ).message_id

    def send_audio(self, chat_id: int, audio_path: str, text: str = None) -> int:
        """
        Отправляет аудио сообщение в чат
        :param chat_id: id чата
        :param text: Текст к аудио. По умолчанию None
        :param audio_path: Путь к аудио файлу
        :return: id сообщения
        """
        with open(audio_path, "rb") as file:
            return self.bot.send_audio(
                chat_id=chat_id,
                audio=file,
                caption=text,
            ).message_id

    def answer_callback(self, callback_id: int | None, text: str, show_alert: bool = True) -> None:
        if callback_id:
            self.bot.answer_callback_query(
                callback_query_id=callback_id,
                text=text,
                show_alert=show_alert
            )
            return
        logging.error("callback_id is None")

    def show_user_ui(
            self,
            user: User,
            text: str,
            *,
            keyboard: InlineKeyboardMarkup | None = None,
            parse_mode: str | None = None,
            disable_web_page_preview: bool = False,
    ) -> None:
        """Изменяет user.ui_msg_id, если его нет или произошла ошибка - отправляет новое сообщение,
        сохраняя его id в user.ui_msg_id.
        """
        ui_msg_id: int | None = user.ui_msg_id
        user_id: int = user.id
        if ui_msg_id:
            # --- 1. пробуем edit ---
            try:
                self.bot.edit_message_text(
                    text,
                    user_id,
                    ui_msg_id,
                    reply_markup=keyboard,
                    parse_mode=parse_mode,
                    disable_web_page_preview=disable_web_page_preview,
                )
                return
            except ApiTelegramException:
                logging.warning(f"Edit failed for msg {ui_msg_id}, sending new")

        # --- 2. fallback → send ---
        msg = self.bot.send_message(
            user_id,
            text,
            reply_markup=keyboard,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
        )
        new_msg_id = msg.message_id

        # --- 3. пытаемся записать ТОЛЬКО если ui_msg_id не изменился ---
        saved = self.user_repo.update_if_field_equals(
            obj_id=user_id,
            field="ui_msg_id",
            old_value=ui_msg_id,
            new_value=new_msg_id
        )

        if not saved:
            # другой поток уже обновил UI → удаляем дубликат
            try:
                self.bot.delete_message(user_id, new_msg_id)
            except Exception:
                pass

    def send_info(
            self,
            chat_id: int,
            game_dir: Path,
            info: dict,
            msg_ids: dict,
            repo: BaseRepository,
            obj_id: int,
            obj_field: str,
            *,
            is_location: bool = False,
    ) -> None:
        text_key = "link" if is_location else "text"
        msg_ids = dict(msg_ids or {})

        # --- TEXT / IMAGE / LOCATION ---
        if not msg_ids.get(text_key):
            text = build_data_text(info) if is_location else info["text"]

            if info.get("image"):
                msg_id: int = self.send_photo(chat_id, text, game_dir / info["image"])
            else:
                if is_location:
                    msg_id: int = self.send_location(chat_id, text)
                else:
                    msg_id: int = self.send_msg(chat_id, text, parse_mode="HTML")

            saved = repo.update_if_key_absent(
                obj_id=obj_id,
                field=obj_field,
                key=text_key,
                value=msg_id
            )
            if not saved:
                try:
                    self.bot.delete_message(chat_id, msg_id)
                except Exception:
                    pass

        # --- AUDIO ---
        if not msg_ids.get("audio") and info.get("audio"):

            msg_id = self.send_audio(chat_id, game_dir / info["audio"])

            saved = repo.update_if_key_absent(
                obj_id=obj_id,
                field=obj_field,
                key="audio",
                value=msg_id
            )
            if not saved:
                try:
                    self.bot.delete_message(chat_id, msg_id)
                except Exception:
                    pass

    def send_player_answer(
            self,
            chat_id: int,
            msg_id: int,
            user_str: str,
            point: Point,
            point_progress_id: int
    ) -> None:
        text = build_answer_text(
            correct_answer=point.answer,
            point_info=f"{point}",
            user_info=f"{user_str}"
        )
        msg = self.bot.copy_message(
            chat_id=INSPECTOR_ID,
            from_chat_id=chat_id,
            message_id=msg_id
        )
        self.bot.send_message(
            chat_id=INSPECTOR_ID,
            text=text,
            reply_to_message_id=msg.message_id,
            reply_markup=review_keyboard(point_progress_id=point_progress_id))

    def send_player_problem(
            self,
            problem_msg: str,
            user_id: int,
            username: str | None,
            full_name: str,
    ) -> None:
        text = build_problem_text(
            problem_msg=problem_msg,
            username=username,
            user_id=user_id,
            full_name=full_name,
        )
        self.bot.send_message(
            chat_id=INSPECTOR_ID,
            text=text,
            parse_mode="HTML"
        )

    def delete_ui_keyboard(self, chat_id, msg_id: int | None) -> None:
        if not msg_id:
            return
        self.bot.edit_message_reply_markup(chat_id, msg_id)
