import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path


if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

MAIN_ADMIN_ID = int(os.getenv("MAIN_ADMIN_ID"))

ADMIN_IDS = {
    int(x)
    for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip()
}
INSPECTOR_ID = int(os.getenv("INSPECTOR_ID"))

BASE_DIR = Path(__file__).resolve().parent.parent
GAMES_DATA_DIR = BASE_DIR / "games_data"
