import enum
from typing import NamedTuple, Type

from . import rank


class EventResult(NamedTuple):
    players: dict[str, "EventPlayerResult"]


class EventPlayerResult:
    def __init__(
        self,
        course_handicap: int,
        front_9_gross: int,
        back_9_gross: int,
        total_gross: int,
        total_net: int,
        below_par_holes: "BelowParHoles"
    ) -> None:
        self.course_handicap = course_handicap
        self.front_9_gross = front_9_gross
        self.back_9_gross = back_9_gross
        self.total_gross = total_gross
        self.total_net = total_net
        self.below_par_holes = below_par_holes
        self.gross_score_points: float = 0.0
        self.net_score_points: float = 0.0
        self.event_points: float = 0.0
        self.gross_score_rank: rank.IEventRank = rank.NoRank()
        self.net_score_rank: rank.IEventRank = rank.NoRank()
        self.event_rank: rank.IEventRank = rank.NoRank()


class BelowParHoleDuplicationError(Exception):
    """Exception to be raised when a hole has already been set with a below par score type."""


class BelowParHoles:
    def __init__(self) -> None:
        self._birdie_holes: set[int] = set()
        self._eagle_holes: set[int] = set()
        self._albatross_holes: set[int] = set()

    def birdie_holes(self) -> set[int]:
        return self._birdie_holes

    def eagle_holes(self) -> set[int]:
        return self._eagle_holes

    def albatross_holes(self) -> set[int]:
        return self._albatross_holes

    def set_hole(self, hole_num: int, score_type: "BelowParScoreType"):
        if self._has_hole_num_been_set(hole_num):
            raise BelowParHoleDuplicationError(f"A below par hole score has alredy been set for hole {hole_num}")

        match score_type:
            case BelowParScoreType.BIRDIE:
                self._birdie_holes.add(hole_num)
            case BelowParScoreType.EAGLE:
                self._eagle_holes.add(hole_num)
            case BelowParScoreType.ALBATROSS:
                self._albatross_holes.add(hole_num)
            case _:
                # This should be unreachable unless a new below par score type is addded.
                raise ValueError(f"Unknown below par score type: {score_type}")

    def _has_hole_num_been_set(self, hole_num: int):
        return hole_num in self._all_hole_nums()

    def _all_hole_nums(self) -> set[int]:
        return self._birdie_holes.union(self._eagle_holes).union(self._albatross_holes)


class BelowParScoreType(enum.Enum):
    BIRDIE = enum.auto()
    EAGLE = enum.auto()
    ALBATROSS = enum.auto()
