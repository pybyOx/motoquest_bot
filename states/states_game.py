from telebot.handler_backends import State, StatesGroup


class BaseStates(StatesGroup):
    @classmethod
    def state(cls, state: State) -> str:
        """Возвращает строковое представление состояния."""
        return str(state)


class GameState(BaseStates):
    waiting_for_answer = State()  # Пользователь отправляет ответ
    waiting_for_review = State()  # Пользователь ждет проверки ответа


class CreateGameStates(BaseStates):
    waiting_for_location = State()
    waiting_for_date = State()


class ErrorStates(BaseStates):
    waiting_for_fix = State()
