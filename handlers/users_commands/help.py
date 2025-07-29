from utils.decorators.log_exceptions import log_exceptions
from loader import bot
from telebot.types import Message


@bot.message_handler(commands=["help"])
@log_exceptions()
def bot_help(message: Message):
    bot.send_message(message.chat.id, "🆘 *Нужна помощь?*\n\n"
                                      "📨 Напишите в поддержку: @tgoxx\n",
                     parse_mode="Markdown")
