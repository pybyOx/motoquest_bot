from bot.loader import bot
from handlers.commands.info import send_info
from telebot.types import CallbackQuery


@bot.callback_query_handler(func=lambda call: call.data == "info")
def call_command_info(callback: CallbackQuery):
    send_info(callback)
