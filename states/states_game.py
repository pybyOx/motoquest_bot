from telebot.handler_backends import State, StatesGroup


class GameState(StatesGroup):
    waiting_for_answer = State()  # Пользователь отправляет ответ
    waiting_for_review = State()  # Пользователь ждет проверки ответа


class CreateGameStates(StatesGroup):
    waiting_for_location = State()
    waiting_for_date = State()


class ErrorStates(StatesGroup):
    waiting_for_fix = State()
