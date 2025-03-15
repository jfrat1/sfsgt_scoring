import enum
from typing import Any, Iterator, NamedTuple

import courses
import season_config
from season_common.player import Player, PlayerGender
from season_common.scorecard import Scorecard


class CourseDataVerificationError(Exception):
    """Exception to be raised when an event's course data does not meet requirements."""


class SeasonModeInputError(Exception):
    pass


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
    scorecard: Scorecard
    player: Player

    @property
    def player_name(self) -> str:
        return self.player.name

    @property
    def is_complete_score(self) -> bool:
        return self.scorecard.is_complete_score()

    @property
    def gender(self) -> PlayerGender:
        return self.player.gender


class SeasonModelEventTees(NamedTuple):
    mens_tee: str
    womens_tee: str

    def tee_for_player(self, gender: PlayerGender) -> str:
        match gender:
            case PlayerGender.MALE:
                return self.mens_tee
            case PlayerGender.FEMALE:
                return self.womens_tee


class SeasonModelEventInput(NamedTuple):
    event_name: str
    course: courses.Course
    tees: SeasonModelEventTees
    event_type: SeasonModelEventType
    players: list[SeasonModelEventPlayerInput]

    @property
    def player_names(self) -> list[str]:
        return [player.player_name for player in self.players]

    def player(self, player_name: str) -> SeasonModelEventPlayerInput:
        for _player in self.players:
            if _player.player_name == player_name:
                return _player

        raise KeyError(f"Player `{player_name} cannot be found.")


class SeasonModelEventInputs:
    def __init__(self, events: list[SeasonModelEventInput]) -> None:
        self._events = events

    @property
    def event_names(self) -> list[str]:
        return [event.event_name for event in self._events]

    def event_input(self, event_name: str) -> SeasonModelEventInput:
        for event in self._events:
            if event.event_name == event_name:
                return event

        raise SeasonModeInputError(f"Event {event_name} could not be found in season model input.")

    def __iter__(self) -> Iterator[SeasonModelEventInput]:
        for event in self._events:
            yield event

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SeasonModelEventInputs):
            return NotImplemented

        return self._events == other._events


class SeasonModelInputConsistencyError(Exception):
    """Exception to be raised when inconsistencies are detected in the season input data."""


class SeasonModelInput:
    def __init__(self, player_names: list[str], events: SeasonModelEventInputs) -> None:
        self._player_names = player_names
        self._events = events

        self._verify_input_consistency()

    @property
    def player_names(self) -> list[str]:
        return self._player_names

    @property
    def event_names(self) -> list[str]:
        return self._events.event_names

    def event_input(self, event_name: str) -> SeasonModelEventInput:
        return self._events.event_input(event_name=event_name)

    def _verify_input_consistency(self) -> None:
        sorted_player_names = sorted(self._player_names)

        for event_data in self._events:
            sorted_event_player_names = sorted(event_data.player_names)
            if sorted_event_player_names != sorted_player_names:
                raise SeasonModelInputConsistencyError(
                    f"Player names in event {event_data.event_name} do not match expectations.\n"
                    f"Expected: {self._player_names}. \nFound: {sorted_event_player_names}."
                )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SeasonModelInput):
            return NotImplemented

        return self._player_names == other._player_names and self._events == other._events
