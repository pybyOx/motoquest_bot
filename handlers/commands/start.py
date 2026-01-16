from bot.loader import bot
from telebot.types import Message
from services.user_actions.start import start_command


@bot.message_handler(commands=["start"])
def bot_start(message: Message):
    start_command(message)
    