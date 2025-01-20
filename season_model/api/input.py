import enum
from typing import Any, Iterator, NamedTuple

import courses
import season_config
from season_common import player, scorecard


class CourseDataVerificationError(Exception):
    """Exception to be raised when an event's course data does not meet requirements."""


class SeasonModelEventType(enum.Enum):
    STANDARD = enum.auto()
    MAJOR = enum.auto()

    @staticmethod
    def from_config_event_type(event_type: season_config.EventType) -> "SeasonModelEventType":
        match event_type:
            case season_config.EventType.STANDARD:
                return SeasonModelEventType.STANDARD
            case season_config.EventType.MAJOR:
                return SeasonModelEventType.MAJOR


class SeasonModelEventPlayerInput(NamedTuple):
    handicap_index: float
    scorecard: scorecard.Scorecard
    player: player.Player

    @property
    def player_name(self) -> str:
        return self.player.name

class SeasonModelEventTees(NamedTuple):
    mens_tee: str
    womens_tee: str

class SeasonModelEventInput(NamedTuple):
    event_name: str
    course: courses.Course
    tees: SeasonModelEventTees
    event_type: SeasonModelEventType
    players: list[SeasonModelEventPlayerInput]

    def player_names(self) -> list[str]:
        return [player.player_name for player in self.players]


class SeasonModelEventInputs:
    def __init__(self, events: list[SeasonModelEventInput]) -> None:
        self.events = events

    def __iter__(self) -> Iterator[SeasonModelEventInput]:
        for event in self.events:
            yield event

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SeasonModelEventInputs):
            return NotImplemented

        return self.events == other.events


class SeasonModelInputConsistencyError(Exception):
    """Exception to be raised when inconsistencies are detected in the season input data."""


class SeasonModelInput:
    def __init__(self, player_names: list[str], events: SeasonModelEventInputs) -> None:
        self._player_names = player_names
        self._events = events

        self._verify_input_consistency()

    def _verify_input_consistency(self) -> None:
        sorted_player_names = sorted(self._player_names)

        for event_data in self._events:
            sorted_event_player_names = sorted(event_data.player_names())
            if sorted_event_player_names != sorted_player_names:
                raise SeasonModelInputConsistencyError(
                    f"Player names in event {event_data.event_name} do not match expectations.\n"
                    f"Expected: {self._player_names}. \nFound: {sorted_event_player_names}."
                )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SeasonModelInput):
            return NotImplemented

        return self._player_names == other._player_names and self._events == other._events
