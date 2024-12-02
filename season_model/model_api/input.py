import enum
from typing import Iterator, NamedTuple

import course_database
from season_common import player, scorecard


class CourseDataVerificationError(Exception):
    """Exception to be raised when an event's course data does not meet requirements."""


class SeasonModelEventType(enum.Enum):
    STANDARD = enum.auto()
    MAJOR = enum.auto()


class SeasonModelEventPlayerInput(NamedTuple):
    handicap_index: float
    scorecard: scorecard.Scorecard
    player: player.Player


class SeasonModelEventInput(NamedTuple):
    course: course_database.Course
    tees: str
    event_type: SeasonModelEventType
    players: list[SeasonModelEventPlayerInput]


class SeasonModelEventInputs(NamedTuple):
    events: list[SeasonModelEventInput]

    # TODO: Test if this even works. I'm not sure.
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
