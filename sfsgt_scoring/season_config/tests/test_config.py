import contextlib
import pathlib
import tempfile
from typing import Generator

import pytest

from .. import config

TEST_SEASON_CONFIG_YAML = """
name: SFSGT 2024
sheet_id: test_sheet_id
players_sheet_name: Handicaps
leaderboard_sheet_name: Leaderboard
events: {
  1: {
    event_name: Poppy Ridge,
    sheet_name: Poppy Ridge,
    course_name: poppy ridge chardonnay/zinfandel,
    tee: white,
    type: standard,
    scorecard_sheet_start_cell: B15
  },
  2: {
    event_name: Presidio,
    sheet_name: Presidio,
    course_name: presidio,
    tee: blue,
    type: standard,
    scorecard_sheet_start_cell: B8
  },
  3: {
    event_name: Harding Park,
    sheet_name: TPC Harding,
    course_name: harding park,
    tee: blue,
    type: major,
    scorecard_sheet_start_cell: B8,
  },
}
"""


@contextlib.contextmanager
def temp_season_config_file(yaml_data: str = TEST_SEASON_CONFIG_YAML) -> Generator[pathlib.Path, None, None]:
    with tempfile.NamedTemporaryFile(suffix=".yaml") as temp_file:
        temp_file_path = pathlib.Path(temp_file.name)
        temp_file_path.write_text(yaml_data)

        yield temp_file_path


def test_load_season_config_file() -> None:
    with temp_season_config_file() as config_file:
        season_config = config.load_season_config_file(config_file)

        assert season_config.name == "SFSGT 2024"
        assert season_config.sheet_id == "test_sheet_id"
        assert season_config.players_sheet_name == "Handicaps"
        assert season_config.leaderboard_sheet_name == "Leaderboard"


TEST_SEASON_CONFIG_YAML_WRONG_EVENT_KEYS = """
name: SFSGT 2024
sheet_id: test_sheet_id
players_sheet_name: Handicaps
leaderboard_sheet_name: Leaderboard
events: {
  1: {
    event_name: Presidio,
    sheet_name: Presidio Scorecard,
    course_name: presidio,
    tee: blue,
    type: standard,
    scorecard_sheet_start_cell: B8,
    not_a_key: Foo Bar,
  },
  3: {
    event_name: Harding Park,
    sheet_name: Harding Park Scorecard,
    course_name: harding park,
    tee: blue,
    type: major,
    scorecard_sheet_start_cell: B8,
    not_a_key: Foo Bar,
  },
}
"""


def test_load_season_config_file_wrong_event_keys_raises_error() -> None:
    with temp_season_config_file(yaml_data=TEST_SEASON_CONFIG_YAML_WRONG_EVENT_KEYS) as config_file:
        with pytest.raises(config.SeasonConfigLoadError):
            config.load_season_config_file(config_file)


EVENT_CONFIG_FOO = config.EventConfig(
    event_name="foo",
    sheet_name="foo sheet",
    course_name="foo course",
    tee="white",
    type=config.EventType.STANDARD,
    scorecard_sheet_start_cell="A1",
)

EVENT_CONFIG_BAR = config.EventConfig(
    event_name="bar",
    sheet_name="bar sheet",
    course_name="bar course",
    tee="white",
    type=config.EventType.STANDARD,
    scorecard_sheet_start_cell="A1",
)


def test_check_events_dict_keys_passes() -> None:
    config.SeasonConfig._check_events_dict_keys({1: EVENT_CONFIG_FOO, 2: EVENT_CONFIG_BAR})


def test_check_events_dict_keys_fails() -> None:
    with pytest.raises(ValueError):
        config.SeasonConfig._check_events_dict_keys({1: EVENT_CONFIG_FOO, 7: EVENT_CONFIG_BAR})


def test_check_event_names_are_unique_passes() -> None:
    config.SeasonConfig._check_event_names_are_unique({1: EVENT_CONFIG_FOO, 2: EVENT_CONFIG_BAR})


def test_check_event_names_are_unique_fails() -> None:
    with pytest.raises(ValueError):
        config.SeasonConfig._check_event_names_are_unique({1: EVENT_CONFIG_FOO, 2: EVENT_CONFIG_FOO})


def test_check_event_sheet_names_are_unique_passes() -> None:
    config.SeasonConfig._check_event_sheet_names_are_unique({1: EVENT_CONFIG_FOO, 2: EVENT_CONFIG_BAR})


def test_check_event_sheet_names_are_unique_fails() -> None:
    with pytest.raises(ValueError):
        config.SeasonConfig._check_event_sheet_names_are_unique({1: EVENT_CONFIG_FOO, 2: EVENT_CONFIG_FOO})


def test_check_event_course_names_are_unique_passes() -> None:
    config.SeasonConfig._check_event_course_names_are_unique({1: EVENT_CONFIG_FOO, 2: EVENT_CONFIG_BAR})


def test_check_event_course_names_are_unique_fails() -> None:
    with pytest.raises(ValueError):
        config.SeasonConfig._check_event_course_names_are_unique({1: EVENT_CONFIG_FOO, 2: EVENT_CONFIG_FOO})


def test_event_names() -> None:
    with temp_season_config_file() as config_file:
        season_config = config.load_season_config_file(config_file)

        assert season_config.event_names() == ["Poppy Ridge", "Presidio", "Harding Park"]


def test_get_event_config() -> None:
    with temp_season_config_file() as config_file:
        season_config = config.load_season_config_file(config_file)

        assert season_config.get_event_config("Presidio") == config.EventConfig(
            event_name="Presidio",
            sheet_name="Presidio",
            course_name="presidio",
            tee="blue",
            type=config.EventType.STANDARD,
            scorecard_sheet_start_cell="B8",
        )


def test_get_event_config_not_found_raises_error() -> None:
    with temp_season_config_file() as config_file:
        season_config = config.load_season_config_file(config_file)

        with pytest.raises(config.SeasonConfigGetEventError):
            season_config.get_event_config("Not an event")
