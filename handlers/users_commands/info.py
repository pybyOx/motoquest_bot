from utils.decorators.log_exceptions import log_exceptions
from utils.decorators.with_context import with_context
from loader import bot
from utils.misc.get_kwargs import get_kwargs
from repositories.repositories import PlayerSessionRepository
from telebot.types import Message


@bot.message_handler(commands=["info"])
def bot_info(message: Message):
    send_info(message)


@with_context(include_player=True)
@log_exceptions()
def send_info(**kwargs):
    chat_id, player = get_kwargs(("chat_id", "player"), kwargs)

    player_sessions = PlayerSessionRepository.filter(player=player, status="registered")
    if not player_sessions:
        bot.send_message(chat_id, "Записей нет. Чтобы записаться, введите команду /register")
        return

    text = 'Вы записаны на:'
    for player_session in player_sessions:
        game_session = player_session.game_session
        text += f'\n\n\t{game_session} {game_session.location}'
    bot.send_message(chat_id, text, parse_mode="HTML", disable_web_page_preview=True)

    # bot.send_message(user_id, "Статистика по пройденным играм:")
    # try:
    #     get_player_session(player_id=user_id, status="finished")
    # except DoesNotExist:
    #     bot.send_message(user_id, "Завершенных игр нет.")
    # else:
    #     pass  # Здесь выводим статистику
