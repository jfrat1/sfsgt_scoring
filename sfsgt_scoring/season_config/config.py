import enum
import pathlib

import pydantic
import pydantic_yaml


class SeasonConfigLoadError(Exception):
    """Exception to be raised when an error is encountered while loading a season config file."""


def load_season_config_file(file_path: pathlib.Path) -> "SeasonConfig":
    try:
        return pydantic_yaml.parse_yaml_file_as(SeasonConfig, file_path)

    except ValueError as exc:
        raise SeasonConfigLoadError(f"Unable to load season config file at {file_path}.") from exc


class SeasonConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True, extra="forbid", strict=True)

    name: str
    sheet_id: str
    players_sheet_name: str
    leaderboard_sheet_name: str
    events: dict[int, "EventConfig"]

    def event_names(self) -> set[str]:
        return {event.event_name for event in self.events.values()}

    @pydantic.field_validator('events')
    @classmethod
    def check_events(cls, events: dict[int, "EventConfig"]) -> dict[int, "EventConfig"]:
        event_count = len(events)
        event_numbers = list(events.keys())
        expected_event_numbers = list(range(1, event_count + 1))
        if event_numbers != expected_event_numbers:
            raise ValueError("Keys in events dict must be start with 1 and increment by 1 for each new event.")

        return events


class EventConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True, extra="forbid")

    event_name: str
    sheet_name: str
    course_name: str
    tee: str
    type: "EventType"
    scorecard_sheet_start_cell: str


class EventType(enum.Enum):
    STANDARD = "standard"
    MAJOR = "major"
