from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class City:
    key: str
    title: str
    timezone: str


class CityEnum(Enum):
    NHA_TRANG = City(
        key="nha_trang",
        title="Нячанг",
        timezone="Asia/Ho_Chi_Minh"
    )
    HANOI = City(
        key="hanoi",
        title="Ханой",
        timezone="Asia/Ho_Chi_Minh"
    )

    @classmethod
    def from_key(cls, key: str) -> City | None:
        for city in cls:
            if city.value.key == key:
                return city.value
        return None
