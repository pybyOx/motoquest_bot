from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GameOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    description: str


class GameShortOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str


class ScheduleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    city: str | None
    date: datetime
    timezone: str | None
    game_info: GameShortOut | None
