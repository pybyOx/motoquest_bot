from bot.loader import bot
from telebot.types import Message
from services.user_actions.cancel import send_player_sessions_keyboard


@bot.message_handler(commands=["cancel"])
def bot_cancel(message: Message):
    send_player_sessions_keyboard(message)
