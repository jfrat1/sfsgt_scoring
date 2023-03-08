from enum import Enum
from typing import List

from ...src.player import Player

JOHN_FRATELLO = Player(
    name="John Fratello",
    handicap=19
)

STANTON_TURNER = Player(
    name="Stanton Turner",
    handicap=18
)

ERIK_PETRICH = Player(
    name="Erik Petrich",
    handicap=19.5
)

class TestPlayers(Enum):
    JohnFratello = JOHN_FRATELLO
    StantonTurner = STANTON_TURNER
    ErikPetrich = ERIK_PETRICH

    @staticmethod
    def to_list() -> List[Player]:
        return [player.value for player in TestPlayers]
