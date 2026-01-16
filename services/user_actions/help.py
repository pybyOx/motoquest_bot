from utils.decorators.log_exceptions import log_exceptions
from utils.decorators.with_context import with_context
from bot.loader import bot
from utils.misc.get_kwargs import get_kwargs


@with_context()
@log_exceptions()
def send_help(**kwargs):
    chat_id = get_kwargs(("chat_id",), kwargs)[0]
    bot.send_message(chat_id, "🆘 *Нужна помощь?*\n\n"
                              "📨 Напишите в поддержку: @tgoxx\n",
                     parse_mode="Markdown")
