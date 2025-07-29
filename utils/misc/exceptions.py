class CreationError(Exception):
    """Ошибка при создании игры, точки или подсказки."""
    pass


class AlreadyExistsError(Exception):
    """Запись с такими ключами уже есть в БД."""
    pass


class CliInputError(Exception):
    """Неверно введена cli-команда."""
    pass


class JSONError(Exception):
    """Неверные данные в json-файле."""
    pass


class DeletionError(Exception):
    """Ошибка удаления объекта peewee."""
    pass
