import logging


logging.basicConfig(
    level=logging.DEBUG,  # Минимальный уровень логирования
    format="%(asctime)s [%(levelname)s] %(message)s",  # Формат логов
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("bot.log", encoding='utf-8'),
              logging.StreamHandler()
              ])

# Подавить лишние отладочные логи
logging.getLogger('peewee').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
