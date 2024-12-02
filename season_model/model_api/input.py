import enum
from typing import Any, Iterator, NamedTuple


class CourseDataVerificationError(Exception):
    """Exception to be raised when an event's course data does not meet requirements."""


class SeasonModelEventCourseTee:
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
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.name == other.name and self.rating == other.rating and self.slope == other.slope


class SeasonModelEventCourseHolePars(dict[int, int]):
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


class SeasonModelEventCourse(NamedTuple):
    name: str
    tee: SeasonModelEventCourseTee
    hole_pars: SeasonModelEventCourseHolePars


class SeasonModelEventType(enum.Enum):
    STANDARD = enum.auto()
    MAJOR = enum.auto()


class SeasonModelEventPlayerInput(NamedTuple):
    pass


class SeasonModelEventInput(NamedTuple):
    course: SeasonModelEventCourse
    event_type: SeasonModelEventType
    players: list[SeasonModelEventPlayerInput]


class SeasonModelEventInputs(NamedTuple):
    events: list[SeasonModelEventInput]

    def __iter__(self) -> Iterator[list[SeasonModelEventInput]]:
        yield self.events


class SeasonModelInputConsistencyError(Exception):
    """Exception to be raised when inconsistencies are detected in the season input data."""


class SeasonModelInput:
    def __init__(self, player_names: list[str], events: SeasonModelEventInputs) -> None:
        self._player_names = player_names
        self._events = events

        self._verify_input_consistency()

    def _verify_input_consistency(self) -> None:
        for event_data in self._events:
            if (event_player_names := event_data.player_names()) != self._player_names:
                raise SeasonModelInputConsistencyError(
                    f"Player names in event {event_data.event_name} do not match expectations.\n"
                    f"Expected: {self._player_names}. \nFound: {event_player_names}."
                )

