from bot.loader import bot
from telebot.types import Message
from services.user_actions.registration import send_sessions_keyboard


@bot.message_handler(commands=["register"])
def bot_register(message: Message):
    send_sessions_keyboard(message)
