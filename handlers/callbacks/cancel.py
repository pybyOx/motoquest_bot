from bot.loader import bot
from telebot.types import CallbackQuery
from services.user_actions.cancel import cancel_player_session, send_player_sessions_keyboard


@bot.callback_query_handler(func=lambda call: call.data == "cancel")
def cb_cancel_start(call: CallbackQuery):
    send_player_sessions_keyboard(call)


@bot.callback_query_handler(func=lambda c: c.data.startswith("cancel:"))
def cb_cancel_confirm(call: CallbackQuery):
    cancel_player_session(call)
