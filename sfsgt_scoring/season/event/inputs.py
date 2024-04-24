import abc
import enum
from typing import Any, NamedTuple


class EventInput(NamedTuple):
    course: "CourseInput"
    type: "EventType"
    players: dict[str, "EventPlayerInput"]

    def player_names(self) -> list[str]:
        return list(self.players.keys())


class EventType(enum.Enum):
    STANDARD = enum.auto()
    MAJOR = enum.auto()


class CourseDataVerificationError(Exception):
    """Exception to be raised when an event's course data does not meet requirements."""


class CourseInput(NamedTuple):
    name: str
    tee: "CourseTeeData"
    hole_pars: "CourseHolePars"


class CourseTeeData:
    COURSE_RATING_MIN = 60.0
    COURSE_RATING_MAX = 80.0
    COURSE_SLOPE_MIN = 55
    COURSE_SLOPE_MAX = 155

    def __init__(self, name: str, rating: float, slope: int) -> None:
        self.name = name
        self.rating = rating
        self.slope = slope

        self._verify()

    def _verify(self) -> None:
        self._verify_rating()
        self._verify_slope()

    def _verify_rating(self) -> None:
        if not (self.COURSE_RATING_MIN < self.rating < self.COURSE_RATING_MAX):
            raise CourseDataVerificationError(
                "Course rating must be in the range: "
                f"[{self.COURSE_RATING_MIN}:{self.COURSE_RATING_MAX}]."
            )

    def _verify_slope(self) -> None:
        if not (self.COURSE_SLOPE_MIN < self.slope < self.COURSE_SLOPE_MAX):
            raise CourseDataVerificationError(
                "Course slope must be in the range: "
                f"[{self.COURSE_SLOPE_MIN}:{self.COURSE_SLOPE_MAX}]."
            )

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

    def total_par(self) -> int:
        return sum(self.values())


class EventPlayerDataVerificationError(Exception):
    """Exception to be raised when a player's event data does not meet requirements."""


class EventPlayerInput(NamedTuple):
    handicap_index: float
    scorecard: "IScorecard"


# TODO: rename to something about "strokes"
class IScorecard(abc.ABC):
    @abc.abstractmethod
    def strokes_per_hole(self) -> dict[int, int]: pass

    @abc.abstractmethod
    def hole_strokes(self, hole_num: int) -> int: pass


class IncompleteScorecardRequestError(Exception):
    """Exception to be raised when requests are made to an incomplete score."""


class IncompleteScorecard(IScorecard):
    def __new__(cls):
        # Implement the singleton pattern for this class because there may be many
        # instances of it and they are stateless/identical.
        if not hasattr(cls, 'instance'):
            cls.instance = super(IncompleteScorecard, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        pass

    def strokes_per_hole(self) -> dict[int, int]:
        raise IncompleteScorecardRequestError(
            "Requests cannot be made to an incomplete score because it does not contain any data"
        )

    def hole_strokes(self, hole_num: int) -> int:
        raise IncompleteScorecardRequestError(
            "Requests cannot be made to an incomplete score because it does not contain any data"
        )


class Scorecard(IScorecard):
    def __init__(self, strokes_per_hole: dict[int, int]) -> None:
        self._strokes_per_hole = strokes_per_hole

    def _verify_keys(self) -> None:
        expected_keys = [hole for hole in range(1, 19)]
        actual_keys = [self._strokes_per_hole.keys()]
        if expected_keys != actual_keys:
            raise EventPlayerDataVerificationError(
                "Keys in the HoleScores dictionary must be integers containing hole numbers 1 through 18. "
                f"\nExpected: {expected_keys}\nFound: {actual_keys}"
            )

    def _verify_values(self) -> None:
        values = self._strokes_per_hole.values()
        are_all_values_int_type = all(isinstance(value, int) for value in values)

        if not are_all_values_int_type:
            raise EventPlayerDataVerificationError(
                f"Values in the HoleScores dictionary must int type. Found: {values}"
            )

    def strokes_per_hole(self) -> dict[int, int]:
        return self._strokes_per_hole

    def hole_strokes(self, hole_num: int) -> int:
        return self._strokes_per_hole[hole_num]

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Scorecard):
            return NotImplemented

        else:
            return self._strokes_per_hole == other._strokes_per_hole
