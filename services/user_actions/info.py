from utils.decorators.log_exceptions import log_exceptions
from utils.decorators.with_context import with_context
from bot.loader import bot
from utils.misc.get_kwargs import get_kwargs
from repositories.repositories import PlayerSessionRepository


@with_context(include_player=True)
@log_exceptions()
def send_info(**kwargs):
    chat_id, player = get_kwargs(("chat_id", "player"), kwargs)

    player_sessions = PlayerSessionRepository.filter(player=player, status="registered")

    text = build_info_text(player_sessions)
    bot.send_message(chat_id, text, parse_mode="HTML", disable_web_page_preview=True)


def build_info_text(player_sessions) -> str:
    if not player_sessions.exists():
        return "Записей нет. Чтобы записаться, введите команду /register"

    lines = ["Вы записаны на:"]
    for ps in player_sessions:
        gs = ps.game_session
        lines.append(f"{gs} {gs.location}")
    return "\n\n".join(lines)
