from urllib.parse import urlsplit

from playhouse.postgres_ext import PostgresqlExtDatabase


def database_params(url: str) -> dict:
    """Разбирает строку подключения в аргументы peewee.

    postgresql://user:password@host:port/name
    """
    parts = urlsplit(url)
    return {
        "database": parts.path.lstrip("/"),
        "user": parts.username,
        "password": parts.password,
        "host": parts.hostname,
        "port": parts.port or 5432,
    }


# База создаётся БЕЗ параметров: импорт этого модуля ничего не читает
# из окружения и никуда не подключается. Модели к ней привязываются как обычно,
# а параметры приходят позже — в setup_db() при старте приложения.
db = PostgresqlExtDatabase(None)
