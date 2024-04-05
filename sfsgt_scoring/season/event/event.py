import enum
from typing import Any, NamedTuple


class EventInput(NamedTuple):
    course: "CourseData"
    type: "EventType"
    players: dict[str, "EventPlayerInput"]


class EventType(enum.Enum):
    STANDARD = enum.auto()
    MAJOR = enum.auto()


class CourseDataVerificationError(Exception):
    """Exception to be raised when an event's course data does not meet requirements."""


class CourseData(NamedTuple):
    name: str
    tee: "CourseTeeData"
    hole_pars: "CourseHolePars"


class CourseTeeData:
    def __init__(self, name: str, rating: float, slope: int) -> None:
        self.name = name
        self.rating = rating
        self.slope = slope

        self._verify()

    def _verify(self) -> None:
        self._verify_rating()
        self._verify_slope()

    def _verify_rating(self) -> None:
        if self.rating < 0:
            raise CourseDataVerificationError("Course rating must be greater than 0.")

    def _verify_slope(self) -> None:
        if self.rating < 0:
            raise CourseDataVerificationError("Course slope must be greater than 0.")

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CourseTeeData):
            return NotImplemented

        return (
            self.name == other.name and
            self.rating == other.rating and
            self.slope == other.slope
        )


class CourseHolePars(dict[int, int]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._verify()

    def _verify(self) -> None:
        self._verify_keys_match_hole_numbers()
        self._verify_values_are_in_range()

    def _verify_keys_match_hole_numbers(self) -> None:
        dict_keys = list(self.keys())
        expected_hole_numbers = list(range(1, 19))
        if not dict_keys == expected_hole_numbers:
            raise CourseDataVerificationError(
                "Keys in the dictionary of course hole pars must be integer numbers 0 through 18."
            )

    def _verify_values_are_in_range(self) -> None:
        allowed_hole_pars = {3, 4, 5}

        for hole_num, hole_par in self.items():
            if hole_par not in allowed_hole_pars:
                raise CourseDataVerificationError(
                    "Values in the dictionary of course hole pars must one of an allowed set of "
                    f"values: {allowed_hole_pars}. Found {hole_par} for hole {hole_num}."
                )


class EventPlayerInput(NamedTuple):
    handicap_index: float
    hole_scores: "HoleScores"


HoleScores = dict[str, int | None]


class EventResult(NamedTuple):
    players: dict[str, "EventPlayerResult"]


class EventPlayerResult(NamedTuple):
    course_handicap: int
    front_9_gross: int
    back_9_gross: int
    total_gross: int
    total_net: int
    gross_score_rank: int
    net_score_rank: int
    gross_score_points: float  # This might not be reuqired right away
    net_score_points: float  # This might not be reuqired right away
    event_points: float
    event_rank: int
    below_par_holes: "BelowParHoles"


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


class Event:
    def __init__(self, input: EventInput) -> None:
        self._input = input

    def results(self) -> EventResult:
        # TODO - start here after refactoring of upstream modules is complete
        return None
