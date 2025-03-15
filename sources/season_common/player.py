import enum
from typing import Any, NamedTuple, Self


class PlayerGender(enum.Enum):
    FEMALE = enum.auto()
    MALE = enum.auto()

    @classmethod
    def _missing_(cls, value: Any) -> Self:
        if not isinstance(value, str):
            return super()._missing_(value)

        for member in cls:
            if member.name.lower() == value.lower():
                return member

        raise ValueError(f"{value} is not a valid member of {cls.__name__}")


class Player(NamedTuple):
    name: str
    gender: PlayerGender
