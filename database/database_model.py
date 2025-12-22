from peewee import (Model, CharField, IntegerField, DateTimeField, TextField, BooleanField, AutoField,
                    ForeignKeyField, DeferredForeignKey)
from playhouse.sqlite_ext import SqliteExtDatabase, JSONField
from datetime import datetime, UTC
from typing import cast


db = SqliteExtDatabase("user_games.db", pragmas={'foreign_keys': 1})


class BaseModel(Model):
    class Meta:
        database = db


class GameInfo(BaseModel):
    """Общая информация об игре."""
    game_id = AutoField()
    title = CharField(unique=True)
    finish = JSONField()  # keys: REQ - "text", "link"

    def __str__(self):
        return f"{self.title}"


class Point(BaseModel):
    """Информация о точках игры."""
    point_id = AutoField()
    title = CharField()
    location = JSONField()  # keys: REQ - "link"; OPT - "text", "voice", "image"

    task = JSONField()  # keys: REQ - "text"; OPT - "voice", "image"
    answer = JSONField()  # keys: REQ - "text", "type"
    after_solved = JSONField()  # keys: REQ - "text"; OPT - "voice", "image"

    game_info = ForeignKeyField(GameInfo, backref="points", on_delete="CASCADE")  # GameInfo.points — все точки игры

    def __str__(self):
        return f"{self.title} ({self.game_info.title})"


class Clue(BaseModel):
    """Подсказки к каждой точке (их 3 максимум)"""
    point = ForeignKeyField(Point, backref="clues", on_delete="CASCADE")
    text = TextField()
    order = IntegerField()  # 1, 2, 3


class GameSession(BaseModel):
    """Информация о конкретной игре с местом и временем проведения."""
    session_id = AutoField()
    game_info = ForeignKeyField(GameInfo, backref="games", null=True, on_delete="SET NULL")
    # GameInfo.games - список всех GameSession c информацией GameInfo

    city = CharField(null=True)  # город проведения игры
    location = CharField()  # место встречи
    date = DateTimeField()  # время встречи
    timezone = CharField(null=True)
    finished = BooleanField(default=False)  # если будет нужно завершить вручную

    class Meta:
        indexes = ((('city', 'date'), True),
                   )

    @property
    def is_finished(self) -> bool:
        """Завершена ли игра: вручную или по дате."""
        return self.finished or self.date < datetime.now(UTC)

    def __str__(self):
        date = cast(datetime, self.date)
        date_str = f"{date.strftime('%d.%m.%Y %H:%M')}"
        city_str = f"📍 {self.city}" if self.city else ""
        return f"{self.game_info.title} {city_str} \n({date_str})"
    

class Player(BaseModel):
    user_id = IntegerField(primary_key=True)
    username = CharField(null=True)
    current_player_session = DeferredForeignKey("PlayerSession", null=True, backref='current_players',
                                                deferrable='INITIALLY DEFERRED', on_delete="SET NULL")
    # PlayerSession.current_players — все Player с конкретным PlayerSession
    current_func = JSONField(null=True)

    def __str__(self):
        return f"{self.username or 'user'} ({self.user_id})"


class PlayerSession(BaseModel):
    """Промежуточная таблица между конкретным игроком и игровой сессией."""
    player_session_id = AutoField()
    player = ForeignKeyField(Player, backref="player_sessions", deferrable='INITIALLY DEFERRED')
    # Player.player_sessions — все PlayerSession с конкретным Player
    game_session = ForeignKeyField(GameSession, backref="player_sessions", on_delete="CASCADE")
    # GameSession.player_sessions — все PlayerSession с конкретной GameSession
    current_point = ForeignKeyField(Point, null=True, backref="current_users", on_delete="SET NULL")
    # Point.current_users - все PlayerSession с конкретным Point
    status = CharField(default="registered")  # варианты: registered, started, finished

    class Meta:
        indexes = (
            (('player', 'game_session'), True),  # уникальность пары (user, game_session)
        )

    def __str__(self):
        return (f"\n GameSession: {self.game_session} (id: {self.game_session.session_id})"
                f"\n Player: {self.player}")


class UserPointProgress(BaseModel):
    """Прохождение пользователем точки в конкретной игре"""
    user_point_progress_id = AutoField()
    player_session = ForeignKeyField(PlayerSession, backref="point_progress", on_delete="CASCADE")
    # UserSession.point_progress - все UserPointProgress с конкретным PlayerSession
    point = ForeignKeyField(Point, backref="users_progress", null=True, on_delete="SET NULL")
    # Point.users_progress — все UserPointProgress с конкретным Point

    started_at = DateTimeField(null=True)
    finished_at = DateTimeField(null=True)
    clues_used = IntegerField(default=0)
    is_finished = BooleanField(default=False)

    @property
    def time(self):
        """Продолжительность прохождения точки (если завершено)"""
        if self.started_at and self.finished_at:
            return self.finished_at - self.started_at
        return None

    class Meta:
        indexes = (
            (('player_session', 'point'), True),
        )

    def __str__(self):
        return (f"\n UserPointProgress: {self.player_session}"
                f"\n Point: {self.point}")


class PlayerEvent(BaseModel):
    player_session = ForeignKeyField(PlayerSession, backref="events", on_delete="CASCADE")
    event_type = CharField()
    created_at = DateTimeField(default=lambda: datetime.now(UTC))

    class Meta:
        indexes = (
            (("player_session", "event_type"), True),
        )


def create_models():
    db.create_tables([GameInfo, Point, Clue,  GameSession, Player, PlayerSession, UserPointProgress, PlayerEvent],
                     safe=True)


def setup_db():
    if db.is_closed():
        db.connect()


def close_db():
    if not db.is_closed():
        db.close()
