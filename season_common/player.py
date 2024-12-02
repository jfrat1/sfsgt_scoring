import enum
from typing import NamedTuple


class PlayerGender(enum.Enum):
    FEMALE = enum.auto()
    MALE = enum.auto()

class Player(NamedTuple):
    name: str
    gender: PlayerGender
