from utils.decorators.log_exceptions import log_exceptions
from utils.decorators.with_context import with_context
from loader import bot


@bot.message_handler(commands=["help"])
@log_exceptions()
@with_context()
def bot_help(**kwargs):

    bot.send_message(kwargs['chat_id'], "🆘 *Нужна помощь?*\n\n"
                                        "📨 Напишите в поддержку: @tgoxx\n",
                     parse_mode="Markdown")
