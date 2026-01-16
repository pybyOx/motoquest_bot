from bot.loader import bot
from telebot.types import CallbackQuery
from services.user_actions.help import send_help


@bot.callback_query_handler(func=lambda call: call.data == "help")
def call_command_help(call: CallbackQuery):
    send_help(call)
