from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.db import get_session
from api.models import GameInfo, GameSession
from api.schemas import GameOut, ScheduleOut


app = FastAPI()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/games", response_model=list[GameOut])
async def list_games(session: SessionDep):
    games = await session.scalars(select(GameInfo).order_by(GameInfo.id))
    return games.all()


@app.get("/schedule", response_model=list[ScheduleOut])
async def list_schedule(session: SessionDep):
    games = await session.scalars(
        select(GameSession)
        .where(GameSession.finished.is_(False), GameSession.date > datetime.now(UTC))
        .order_by(GameSession.date)
        .options(selectinload(GameSession.game_info))
    )
    return games.all()
