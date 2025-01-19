import enum
import pathlib
from typing import Optional

import pydantic
import pydantic_yaml

SEASON_CONFIG_PATH = pathlib.Path(__file__).parent / "seasons"


class SeasonConfigFileNotFoundError(Exception):
    """Exception to be raised when an error encountered while loading a season config."""


class SeasonConfigLoadError(Exception):
    """Exception to be raised when an error is encountered while loading a season config file."""


class SeasonConfigGetEventError(Exception):
    """Exception to be raised when an error is encountered while getting an event by name."""


def load_season_config(season: str) -> "SeasonConfig":
    """Load a season configuration from a prespecified directory containing config YAML files.

    Args:
        season (str): The config to be loaded from the season configs directory. This must match
            the name of a file in the configs directory without the .yaml extension.
            For example: season="2024" will search for "2024.yaml".

    Raises:
        SeasonConfigFileNotFoundError: If the specified season config file cannot be found.
    """
    season_config_file_name = season + ".yaml"
    season_config_file = SEASON_CONFIG_PATH / season_config_file_name
    if not season_config_file.is_file():
        raise SeasonConfigFileNotFoundError(f"Can't locate season config file at: {season_config_file}.")

    return load_season_config_file(file_path=season_config_file)


def load_season_config_file(file_path: pathlib.Path) -> "SeasonConfig":
    try:
        return pydantic_yaml.parse_yaml_file_as(SeasonConfig, file_path)

    except ValueError as exc:
        raise SeasonConfigLoadError(f"Unable to load season config file at {file_path}.") from exc


class FinaleSheetConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True, extra="forbid", strict=True)

    enabled: bool
    sheet_name: str


class SeasonConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True, extra="forbid", strict=True)

    name: str
    sheet_id: str
    players_sheet_name: str
    leaderboard_sheet_name: str
    finale_handicaps_sheet: FinaleSheetConfig
    events: dict[int, "EventConfig"]

    def event_names(self) -> list[str]:
        return [event.event_name for event in self.events.values()]

    def event_configs(self) -> dict[int, "EventConfig"]:
        return self.events

    def get_event_config(self, event_name: str) -> "EventConfig":
        candidate_events = [event for event in self.events.values() if event.event_name == event_name]
        if len(candidate_events) == 0:
            raise SeasonConfigGetEventError(f"No events can be found with name {event_name}")
        if len(candidate_events) > 1:
            # Due to validation of unique event names below, this should not be possible to reach.
            raise SeasonConfigGetEventError(f"More than 1 event with name '{event_name}' found in config.")

        return candidate_events[0]

    def is_finale_enabled(self) -> bool:
        return self.finale_handicaps_sheet.enabled

    @pydantic.field_validator("events")
    @classmethod
    def _check_events(cls, events: dict[int, "EventConfig"]) -> dict[int, "EventConfig"]:
        cls._check_events_dict_keys(events)
        cls._check_event_names_are_unique(events)
        cls._check_event_sheet_names_are_unique(events)
        cls._check_event_course_names_are_unique(events)

        return events

    @classmethod
    def _check_events_dict_keys(cls, events: dict[int, "EventConfig"]):
        event_count = len(events)
        event_numbers = list(events.keys())
        expected_event_numbers = list(range(1, event_count + 1))
        if event_numbers != expected_event_numbers:
            raise ValueError("Keys in events dict must be start with 1 and increment by 1 for each new event.")

    @classmethod
    def _check_event_names_are_unique(cls, events: dict[int, "EventConfig"]):
        event_names_list = [event.event_name for event in events.values()]
        event_names_deduplicated = list(set(event_names_list))

        if sorted(event_names_list) != sorted(event_names_deduplicated):
            raise ValueError("Event names in the events dictionary must be unique.")

    @classmethod
    def _check_event_sheet_names_are_unique(cls, events: dict[int, "EventConfig"]):
        event_sheet_names_list = [event.sheet_name for event in events.values()]
        event_sheet_names_deduplicated = list(set(event_sheet_names_list))

        if sorted(event_sheet_names_list) != sorted(event_sheet_names_deduplicated):
            raise ValueError("Event names in the events dictionary must be unique.")

    @classmethod
    def _check_event_course_names_are_unique(cls, events: dict[int, "EventConfig"]):
        event_course_names_list = [event.course_name for event in events.values()]
        event_course_names_deduplicated = list(set(event_course_names_list))

        if sorted(event_course_names_list) != sorted(event_course_names_deduplicated):
            raise ValueError("Event names in the events dictionary must be unique.")


class EventTeeConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True, extra="forbid")

    mens_tee: str
    womens_tee: Optional[str] = None


class EventType(enum.Enum):
    STANDARD = "standard"
    MAJOR = "major"


class EventConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True, extra="forbid")

    event_name: str
    sheet_name: str
    course_name: str
    tees: EventTeeConfig
    type: EventType
    scorecard_sheet_start_cell: str
