

class AlreadyExistsError(Exception):
    """Запись с такими ключами уже есть в БД."""
    pass


class CliInputError(Exception):
    """Неверно введена cli-команда."""
    pass


class DeletionError(Exception):
    """Ошибка удаления объекта peewee."""
    pass


class GameInvariantError(RuntimeError):
    """Нарушен инвариант состояния игры."""
    USER_REQUIRED = "Отсутствует User внутри активной игровой сессии."
    USER_SESSION_REQUIRED = "Отсутствует UserSession внутри активной игровой сессии."
    USER_SESSION_FINISHED = "Устаревший UserSession внутри активной игровой сессии."
    POINT_PROGRESS_REQUIRED = "Отсутствует PointProgress внутри активной игровой сессии."
    CURRENT_POINT_REQUIRED = "Отсутствует текущая Point внутри активной игровой сессии."
    GAME_STATE_REQUIRED = "Отсутствует GameState внутри активной игровой сессии."
