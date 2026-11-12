"""Одноразовый перенос данных из user_games.db (SQLite) в PostgreSQL.

Запуск:
    python -m scripts.migrate_sqlite_to_postgres

Адрес PostgreSQL берётся из DATABASE_URL, как и у бота. Скрипт отказывается
работать, если в целевой базе уже есть данные, — чтобы повторный запуск
не создал дубликаты.
"""

import json
import sqlite3
import sys
from datetime import datetime

from psycopg2.extras import Json

from config_data.config import BASE_DIR
from database.db import db
from database.lifecycle import close_db, create_models, setup_db

SQLITE_PATH = BASE_DIR / "user_games.db"

# Порядок важен: сначала таблицы, на которые ссылаются, потом ссылающиеся.
TABLES = [
    "user",
    "gameinfo",
    "point",
    "clue",
    "gamesession",
    "usersession",
    "pointprogress",
    "userevent",
    "admindraft",
]


def column_types(table: str) -> dict[str, str]:
    """Типы колонок целевой таблицы — по ним решаем, как преобразовать значение."""
    rows = db.execute_sql(
        "select column_name, data_type from information_schema.columns "
        "where table_schema = 'public' and table_name = %s",
        (table,),
    ).fetchall()
    return dict(rows)


def convert(value, pg_type: str):
    """Приводит значение из SQLite к типу колонки PostgreSQL."""
    if value is None:
        return None
    if pg_type == "jsonb":
        # в SQLite JSON лежит текстом
        return Json(json.loads(value) if isinstance(value, str) else value)
    if pg_type == "timestamp with time zone":
        return datetime.fromisoformat(value) if isinstance(value, str) else value
    if pg_type == "boolean":
        # в SQLite булево — это 0 или 1
        return bool(value)
    return value


def target_is_empty() -> bool:
    for table in TABLES:
        count = db.execute_sql(f'select count(*) from "{table}"').fetchone()[0]
        if count:
            print(f"⛔ В таблице {table} уже есть строки ({count}). Перенос отменён.")
            return False
    return True


def reset_sequence(table: str) -> None:
    """Сдвигает счётчик автоинкремента за максимальный перенесённый id.

    Без этого следующая вставка получит id = 1 и упадёт на уникальности.
    """
    db.execute_sql(
        f"""
        select setval(
            pg_get_serial_sequence('"{table}"', 'id'),
            coalesce((select max(id) from "{table}"), 1),
            (select count(*) from "{table}") > 0
        )
        """
    )


def migrate() -> None:
    if not SQLITE_PATH.exists():
        sys.exit(f"Файл {SQLITE_PATH} не найден")

    setup_db()
    create_models()

    if not target_is_empty():
        close_db()
        sys.exit(1)

    source = sqlite3.connect(SQLITE_PATH)
    source.row_factory = sqlite3.Row

    print(f"{'таблица':16} {'перенесено':>10} {'в источнике':>12}")
    with db.atomic():
        for table in TABLES:
            rows = source.execute(f'select * from "{table}"').fetchall()
            if rows:
                types = column_types(table)
                columns = list(rows[0].keys())
                quoted = ", ".join(f'"{c}"' for c in columns)
                placeholders = ", ".join(["%s"] * len(columns))
                for row in rows:
                    values = [convert(row[c], types[c]) for c in columns]
                    db.execute_sql(
                        f'insert into "{table}" ({quoted}) values ({placeholders})', values
                    )
            if "id" in (rows[0].keys() if rows else []):
                reset_sequence(table)

            moved = db.execute_sql(f'select count(*) from "{table}"').fetchone()[0]
            print(f"{table:16} {moved:>10} {len(rows):>12}")

    source.close()
    close_db()
    print("\nГотово.")


if __name__ == "__main__":
    migrate()
