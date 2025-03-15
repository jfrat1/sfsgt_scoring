import enum
from typing import Any


class NotableHoleDuplicationError(Exception):
    """Exception to be raised when a hole has already been set with a notable hole score type."""


class UnknownHoleNumberError(Exception):
    """Exception to be raised when a client sets or requests a hole number that doesn't exist."""


HOLE_NUMBERS = range(1, 19)


class NotableHoleType(enum.Enum):
    NONE = enum.auto()
    BIRDIE = enum.auto()
    EAGLE = enum.auto()
    ALBATROSS = enum.auto()
    OVER_MAX = enum.auto()


class NotableHoles:
    def __init__(self) -> None:
        self._holes: dict[int, NotableHoleType] = {hole_num: NotableHoleType.NONE for hole_num in HOLE_NUMBERS}

    def birdie_holes(self) -> list[int]:
        return self._hole_numbers_matching_type(NotableHoleType.BIRDIE)

    def eagle_holes(self) -> list[int]:
        return self._hole_numbers_matching_type(NotableHoleType.EAGLE)

    def albatross_holes(self) -> list[int]:
        return self._hole_numbers_matching_type(NotableHoleType.ALBATROSS)

    def over_max_holes(self) -> list[int]:
        return self._hole_numbers_matching_type(NotableHoleType.OVER_MAX)

    def num_birdies(self) -> int:
        return len(self.birdie_holes())

    def num_eagles(self) -> int:
        return len(self.eagle_holes())

    def num_albatrosses(self) -> int:
        return len(self.albatross_holes())

    def set_hole(self, hole_num: int, hole_type: NotableHoleType) -> None:
        self._verify_hole_number(hole_num)

        if self._has_hole_num_been_set(hole_num):
            raise NotableHoleDuplicationError(f"A notable hole score has alredy been set for hole {hole_num}")

        self._set_hole_type(hole_num=hole_num, hole_type=hole_type)

    def _hole_numbers_matching_type(self, match_hole_type: NotableHoleType) -> list[int]:
        return [hole_num for hole_num, hole_type in self._holes.items() if hole_type == match_hole_type]

    def _get_hole_type(self, hole_num: int) -> NotableHoleType:
        self._verify_hole_number(hole_num)
        return self._holes[hole_num]

    def _set_hole_type(self, hole_num: int, hole_type: NotableHoleType) -> None:
        self._verify_hole_number(hole_num)
        self._holes[hole_num] = hole_type

    def _verify_hole_number(self, hole_num: int) -> None:
        if hole_num not in HOLE_NUMBERS:
            raise UnknownHoleNumberError(f"Unknown hole number {hole_num}. It must be an integer in the range 0 to 18.")

    def _has_hole_num_been_set(self, hole_num: int):
        return self._get_hole_type(hole_num) is not NotableHoleType.NONE

    def _all_hole_nums(self) -> list[int]:
        return [hole_num for hole_num, hole_type in self._holes.items() if hole_type != NotableHoleType.NONE]

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self._holes == other._holes

    def __repr__(self) -> str:
        attributes = self.__dict__
        # Attribute names need to have their prefix underscore removed.
        attributes_string = ", ".join([f"{name.lstrip("_")}: {value}" for name, value in attributes.items()])
        return f"{self.__class__.__name__}({attributes_string})"
