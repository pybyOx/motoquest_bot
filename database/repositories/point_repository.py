from database.models.point import Point
from database.repositories.base_repository import BaseRepository


class PointRepository(BaseRepository[Point]):
    def __init__(self):
        super().__init__(Point)
