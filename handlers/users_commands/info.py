from utils.decorators.log_exceptions import log_exceptions
from loader import bot
from telebot.types import Message
from peewee import DoesNotExist
from repositories.repositories import PlayerSessionRepository, PlayerRepository


@bot.message_handler(commands=["info"])
@log_exceptions()
def bot_info(message: Message):
    send_info(message.from_user.id)


def send_info(user_id: int):
    try:
        player = PlayerRepository.get(user_id=user_id)
    except DoesNotExist:
        bot.send_message(user_id, "Сначала нужно зарегистрироваться, введя команду /start")
        return

    player_sessions = PlayerSessionRepository.filter(player=player, status="registered")
    if not player_sessions:
        bot.send_message(user_id, "Записей нет. Чтобы записаться, введите команду /register")
        return

    bot.send_message(user_id, "\tВы записаны на:")
    for player_session in player_sessions:
        game_session = player_session.game_session
        bot.send_message(user_id, f"\n\t{game_session}.\nЛокация: {game_session.location}")

    # bot.send_message(user_id, "Статистика по пройденным играм:")
    # try:
    #     get_player_session(player_id=user_id, status="finished")
    # except DoesNotExist:
    #     bot.send_message(user_id, "Завершенных игр нет.")
    # else:
    #     pass  # Здесь выводим статистику
