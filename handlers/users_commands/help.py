from utils.decorators.log_exceptions import log_exceptions
from utils.decorators.with_context import with_context
from loader import bot


@bot.message_handler(commands=["help"])
@with_context()
@log_exceptions()
def bot_help(**kwargs):

    bot.send_message(kwargs['chat_id'], "🆘 *Нужна помощь?*\n\n"
                                        "📨 Напишите в поддержку: @tgoxx\n",
                     parse_mode="Markdown")
