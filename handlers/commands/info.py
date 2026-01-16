from bot.loader import bot
from telebot.types import Message
from services.user_actions.info import send_info


@bot.message_handler(commands=["info"])
def bot_info(message: Message):
    send_info(message)
