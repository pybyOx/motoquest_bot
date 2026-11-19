from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db import get_session
from api.models import GameInfo
from api.schemas import GameOut


app = FastAPI()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/games", response_model=list[GameOut])
async def list_games(session: SessionDep):
    games = await session.scalars(select(GameInfo).order_by(GameInfo.id))
    return games.all()
