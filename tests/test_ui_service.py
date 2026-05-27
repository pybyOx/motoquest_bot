from unittest.mock import MagicMock, patch
from telebot.apihelper import ApiTelegramException
from services.ui_service import UIService


# ── send_msg ───────────────────────────────────────────────────────────

def test_send_msg_returns_message_id():
    bot = MagicMock()
    bot.send_message.return_value.message_id = 99
    user_repo = MagicMock()

    service = UIService(bot=bot, user_repo=user_repo)

    result = service.send_msg(chat_id=123, text="привет")

    assert result == 99
    bot.send_message.assert_called_once_with(
        123, "привет",
        reply_to_message_id=None,
        reply_markup=None,
        parse_mode=None,
        disable_web_page_preview=False,
    )


# ── show_user_ui ───────────────────────────────────────────────────────────

def test_show_user_ui_edit_success():
    bot = MagicMock()
    user_repo = MagicMock()
    service = UIService(bot=bot, user_repo=user_repo)

    user = MagicMock()
    user.id = 1
    user.ui_msg_id = 100

    service.show_user_ui(user, "текст")

    bot.edit_message_text.assert_called_once_with(
        "текст", 1, 100,
        reply_markup=None,
        parse_mode=None,
        disable_web_page_preview=False,
    )
    bot.send_message.assert_not_called()
    user_repo.update_if_field_equals.assert_not_called()


def test_show_user_ui_edit_fell():
    # arrange:
    bot = MagicMock()
    bot.edit_message_text.side_effect = ApiTelegramException(
        "edit_message_text", 400, {"error_code": 400, "description": "Bad Request"})
    bot.send_message.return_value.message_id = 200

    user_repo = MagicMock()
    user_repo.update_if_field_equals.return_value = True

    user = MagicMock()
    user.id = 1
    user.ui_msg_id = 100

    service = UIService(bot=bot, user_repo=user_repo)

    service.show_user_ui(user, "текст")

    bot.edit_message_text.assert_called_once_with(
            "текст", 1, 100,
            reply_markup=None,
            parse_mode=None,
            disable_web_page_preview=False,
        )
    bot.send_message.assert_called_once_with(
        1, "текст",
        reply_markup=None,
        parse_mode=None,
        disable_web_page_preview=False,
    )
    user_repo.update_if_field_equals.assert_called_once_with(
        obj_id=1,
        field="ui_msg_id",
        old_value=100,
        new_value=200
    )
    bot.delete_message.assert_not_called()


def test_show_user_ui_cas_failed_deletes_duplicate():
    # arrange:
    bot = MagicMock()
    bot.edit_message_text.side_effect = ApiTelegramException(
        "edit_message_text", 400, {"error_code": 400, "description": "Bad Request"})
    bot.send_message.return_value.message_id = 200

    user_repo = MagicMock()
    user_repo.update_if_field_equals.return_value = False

    user = MagicMock()
    user.id = 1
    user.ui_msg_id = 100

    service = UIService(bot=bot, user_repo=user_repo)

    service.show_user_ui(user, "текст")

    bot.edit_message_text.assert_called_once_with(
            "текст", 1, 100,
            reply_markup=None,
            parse_mode=None,
            disable_web_page_preview=False,
        )
    bot.send_message.assert_called_once_with(
        1, "текст",
        reply_markup=None,
        parse_mode=None,
        disable_web_page_preview=False,
    )
    user_repo.update_if_field_equals.assert_called_once_with(
        obj_id=1,
        field="ui_msg_id",
        old_value=100,
        new_value=200
    )
    bot.delete_message.assert_called_once_with(1, 200)


def test_show_user_ui_no_existing_msg_sends_new():
    # arrange:
    bot = MagicMock()
    bot.send_message.return_value.message_id = 200

    user_repo = MagicMock()
    user_repo.update_if_field_equals.return_value = True

    user = MagicMock()
    user.id = 1
    user.ui_msg_id = None

    service = UIService(bot=bot, user_repo=user_repo)

    service.show_user_ui(user, "текст")

    bot.send_message.assert_called_once_with(
        1, "текст",
        reply_markup=None,
        parse_mode=None,
        disable_web_page_preview=False,
    )
    user_repo.update_if_field_equals.assert_called_once_with(
        obj_id=1,
        field="ui_msg_id",
        old_value=None,
        new_value=200
    )
    bot.delete_message.assert_not_called()


# ── send_location ─────────────────────────────────────────────────────────────

def test_send_location_with_msg_id_edits():
    bot = MagicMock()
    bot.edit_message_text.return_value.message_id = 100
    service = UIService(bot=bot, user_repo=MagicMock())

    result = service.send_location(chat_id=1, location="ссылка", msg_id=100)

    assert result == 100
    bot.edit_message_text.assert_called_once_with(
        "ссылка", 1, 100,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    bot.send_message.assert_not_called()


def test_send_location_without_msg_id_sends():
    bot = MagicMock()
    bot.send_message.return_value.message_id = 55
    service = UIService(bot=bot, user_repo=MagicMock())

    result = service.send_location(chat_id=1, location="ссылка")

    assert result == 55
    bot.send_message.assert_called_once_with(
        1, "ссылка",
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    bot.edit_message_text.assert_not_called()


# ── answer_callback ───────────────────────────────────────────────────────────

def test_answer_callback_calls_bot():
    bot = MagicMock()
    service = UIService(bot=bot, user_repo=MagicMock())

    service.answer_callback(callback_id=42, text="ок")

    bot.answer_callback_query.assert_called_once_with(
        callback_query_id=42,
        text="ок",
        show_alert=True,
    )


def test_answer_callback_none_id_does_nothing():
    bot = MagicMock()
    service = UIService(bot=bot, user_repo=MagicMock())

    service.answer_callback(callback_id=None, text="ок")

    bot.answer_callback_query.assert_not_called()


# ── send_photo ───────────────────────────────────────────────────────────

def test_send_photo_returns_message_id():
    bot = MagicMock()
    bot.send_photo.return_value.message_id = 77
    service = UIService(bot=bot, user_repo=MagicMock())

    with patch("builtins.open", MagicMock()):
        result = service.send_photo(chat_id=1, text="фото", image_path="img.jpg")

    assert result == 77


# ── send_audio ───────────────────────────────────────────────────────────

def test_send_audio_returns_message_id():
    bot = MagicMock()
    bot.send_audio.return_value.message_id = 88
    service = UIService(bot=bot, user_repo=MagicMock())

    with patch("builtins.open", MagicMock()):
        result = service.send_audio(chat_id=1, audio_path="audio.mp3")

    assert result == 88
    bot.send_audio.assert_called_once()


# ── send_player_answer ────────────────────────────────────────────────────────

def test_send_player_answer_copies_and_sends():
    bot = MagicMock()
    bot.copy_message.return_value.message_id = 300
    service = UIService(bot=bot, user_repo=MagicMock())

    point = MagicMock()
    point.answer = {"type": "текст", "text": "42"}

    service.send_player_answer(
        chat_id=1, msg_id=10, user_str="Оксана", point=point, point_progress_id=5
    )

    bot.copy_message.assert_called_once()
    bot.send_message.assert_called_once()
    assert bot.send_message.call_args.kwargs["reply_to_message_id"] == 300


# ── send_player_problem ───────────────────────────────────────────────────────

def test_send_player_problem_sends_to_inspector():
    bot = MagicMock()
    service = UIService(bot=bot, user_repo=MagicMock())

    service.send_player_problem(
        problem_msg="сломалось", user_id=1, username="ox", full_name="Оксана"
    )

    bot.send_message.assert_called_once()
    assert bot.send_message.call_args.kwargs["parse_mode"] == "HTML"


# ── delete_ui_keyboard ────────────────────────────────────────────────────────

def test_delete_ui_keyboard_calls_edit():
    bot = MagicMock()
    service = UIService(bot=bot, user_repo=MagicMock())

    service.delete_ui_keyboard(chat_id=1, msg_id=50)

    bot.edit_message_reply_markup.assert_called_once_with(1, 50)


def test_delete_ui_keyboard_none_msg_id_does_nothing():
    bot = MagicMock()
    service = UIService(bot=bot, user_repo=MagicMock())

    service.delete_ui_keyboard(chat_id=1, msg_id=None)

    bot.edit_message_reply_markup.assert_not_called()