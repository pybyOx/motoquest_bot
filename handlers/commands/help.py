from bot.loader import bot
from services.user_actions.help import send_help
from telebot.types import Message


@bot.message_handler(commands=["help"])
def bot_help(message: Message):
    send_help(message)
