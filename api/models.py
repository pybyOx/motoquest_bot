from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Общий предок всех моделей API — через него Alembic увидит все таблицы."""


class GameInfo(Base):
    __tablename__ = "gameinfo"
    __table_args__ = (
        Index("gameinfo_title", "title", unique=True),
        Index("gameinfo_slug", "slug", unique=True),
        Index("gameinfo_finish", "finish", postgresql_using="gin"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255))
    finish: Mapped[dict] = mapped_column(JSONB)
    description: Mapped[str] = mapped_column(Text, server_default="")
    points: Mapped[list["Point"]] = relationship(back_populates="game_info")
    game_sessions: Mapped[list["GameSession"]] = relationship(back_populates="game_info")


class Point(Base):
    __tablename__ = "point"
    __table_args__ = (
        Index("point_game_info_id", "game_info_id"),
        Index("point_location", "location", postgresql_using="gin"),
        Index("point_task", "task", postgresql_using="gin"),
        Index("point_answer", "answer", postgresql_using="gin"),
        Index("point_after_solved", "after_solved", postgresql_using="gin"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    location: Mapped[dict] = mapped_column(JSONB)
    task: Mapped[dict] = mapped_column(JSONB)
    answer: Mapped[dict] = mapped_column(JSONB)
    after_solved: Mapped[dict] = mapped_column(JSONB)
    game_info_id: Mapped[int] = mapped_column(
        ForeignKey("gameinfo.id", ondelete="CASCADE")
    )
    game_info: Mapped["GameInfo"] = relationship(back_populates="points")
    clues: Mapped[list["Clue"]] = relationship(back_populates="point", order_by="Clue.order")


class Clue(Base):
    """Подсказка к точке; order — порядок выдачи внутри точки."""

    __tablename__ = "clue"
    __table_args__ = (
        Index("clue_point_id", "point_id"),
        Index("clue_point_id_order", "point_id", "order", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    point_id: Mapped[int] = mapped_column(ForeignKey("point.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(Text)
    order: Mapped[int]
    point: Mapped["Point"] = relationship(back_populates="clues")


class GameSession(Base):
    """Конкретная игра в расписании: город, место, дата."""

    __tablename__ = "gamesession"
    __table_args__ = (
        Index("gamesession_game_info_id", "game_info_id"),
        Index("gamesession_city_date", "city", "date", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    game_info_id: Mapped[int | None] = mapped_column(
        ForeignKey("gameinfo.id", ondelete="SET NULL")
    )
    city: Mapped[str | None] = mapped_column(String(255))
    location: Mapped[str] = mapped_column(String(255))
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    timezone: Mapped[str | None] = mapped_column(String(255))
    finished: Mapped[bool] = mapped_column(Boolean)
    game_info: Mapped["GameInfo | None"] = relationship(back_populates="game_sessions")


class User(Base):
    """Пользователь бота; id — Telegram ID, поэтому без автоинкремента."""

    __tablename__ = "user"
    __table_args__ = (
        Index("user_current_user_session_id", "current_user_session_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    username: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(255))
    state: Mapped[str] = mapped_column(String(255))
    recovery_attempts: Mapped[int]
    is_error: Mapped[bool] = mapped_column(Boolean)
    ui_msg_id: Mapped[int | None]
    # В базе это просто число с индексом, без внешнего ключа (так создал peewee).
    current_user_session_id: Mapped[int | None]


class UserSession(Base):
    """Участие пользователя в конкретной игре."""

    __tablename__ = "usersession"
    __table_args__ = (
        Index("usersession_user_id", "user_id"),
        Index("usersession_game_session_id", "game_session_id"),
        Index("usersession_current_point_id", "current_point_id"),
        Index("usersession_user_id_game_session_id", "user_id", "game_session_id", unique=True),
        Index("usersession_finish_msg_ids", "finish_msg_ids", postgresql_using="gin"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", deferrable=True, initially="DEFERRED")
    )
    game_session_id: Mapped[int] = mapped_column(
        ForeignKey("gamesession.id", ondelete="CASCADE")
    )
    current_point_id: Mapped[int | None] = mapped_column(
        ForeignKey("point.id", ondelete="SET NULL")
    )
    state: Mapped[str] = mapped_column(String(255))
    finish_msg_ids: Mapped[list] = mapped_column(JSONB)


class UserEvent(Base):
    """Разовое событие внутри участия (например, «показан финал»)."""

    __tablename__ = "userevent"
    __table_args__ = (
        Index("userevent_user_session_id", "user_session_id"),
        Index("userevent_user_session_id_event_type", "user_session_id", "event_type", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_session_id: Mapped[int] = mapped_column(
        ForeignKey("usersession.id", ondelete="CASCADE")
    )
    event_type: Mapped[str] = mapped_column(String(255))


class PointProgress(Base):
    """Прохождение одной точки в рамках участия."""

    __tablename__ = "pointprogress"
    __table_args__ = (
        Index("pointprogress_user_session_id", "user_session_id"),
        Index("pointprogress_point_id", "point_id"),
        Index("pointprogress_user_session_id_point_id", "user_session_id", "point_id", unique=True),
        Index("pointprogress_location_msg_ids", "location_msg_ids", postgresql_using="gin"),
        Index("pointprogress_task_msg_ids", "task_msg_ids", postgresql_using="gin"),
        Index("pointprogress_solved_msg_ids", "solved_msg_ids", postgresql_using="gin"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_session_id: Mapped[int] = mapped_column(
        ForeignKey("usersession.id", ondelete="CASCADE")
    )
    point_id: Mapped[int | None] = mapped_column(ForeignKey("point.id", ondelete="SET NULL"))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    location_msg_ids: Mapped[list] = mapped_column(JSONB)
    task_msg_ids: Mapped[list] = mapped_column(JSONB)
    solved_msg_ids: Mapped[list] = mapped_column(JSONB)
    clues_used: Mapped[int]
    is_finished: Mapped[bool] = mapped_column(Boolean)
    answer_error: Mapped[bool] = mapped_column(Boolean)


class AdminDraft(Base):
    """Черновик создания игры организатором; ключ — Telegram ID организатора."""

    __tablename__ = "admindraft"
    __table_args__ = (
        Index("admindraft_game_info_id", "game_info_id"),
        Index("admindraft_game_session_id", "game_session_id"),
    )

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    game_info_id: Mapped[int | None] = mapped_column(ForeignKey("gameinfo.id"))
    city: Mapped[str | None] = mapped_column(String(255))
    timezone: Mapped[str | None] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(Text)
    date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    game_session_id: Mapped[int | None] = mapped_column(
        ForeignKey("gamesession.id", ondelete="SET NULL")
    )
