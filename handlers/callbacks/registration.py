from bot.loader import bot
from services.user_actions.registration import send_sessions_keyboard, call_register
from telebot.types import CallbackQuery


@bot.callback_query_handler(func=lambda call: call.data == "register")
def cd_registration_start(call: CallbackQuery):
    send_sessions_keyboard(call)


@bot.callback_query_handler(func=lambda c: c.data.startswith("register:"))
def cd_registration_confirm(call: CallbackQuery):
    call_register(call)
