import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))

PLAYER_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Написать в поддержку"),
    ("register", "Записаться на игру"),
    ("cancel", "Отменить запись"),
    ("info", "Информация о ваших играх")
)
ADMIN_COMMANDS = (
    ("create_game", "Создать сессию"),
    ("manage_game", "Управлять сессией")
)
