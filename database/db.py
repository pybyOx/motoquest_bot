from playhouse.sqlite_ext import SqliteExtDatabase
from config_data.config import BASE_DIR

db = SqliteExtDatabase(BASE_DIR/"user_games.db", pragmas={'foreign_keys': 1})
