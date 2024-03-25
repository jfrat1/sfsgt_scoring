import contextlib
import pathlib
import tempfile
from typing import Generator

import pytest

from sfsgt_scoring.season_config import config

TEST_SEASON_CONFIG_YAML = """
name: SFSGT 2024
sheet_id: test_sheet_id
players_sheet_name: Player Handicaps
leaderboard_sheet_name: Leaderboard
events: {
  1: {
    event_name: Presidio,
    sheet_name: Presidio Scorecard,
    course_name: presidio,
    tee: blue,
    type: standard,
    scorecard_sheet_start_cell: B8
  },
  2: {
    event_name: Poppy Ridge,
    sheet_name: Poppy Ridge Scorecard,
    course_name: poppy ridge zinfandel/merlot,
    tee: white,
    type: standard,
    scorecard_sheet_start_cell: B15
  },
  3: {
    event_name: Harding Park,
    sheet_name: Harding Park Scorecard,
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
        assert season_config.players_sheet_name == "Player Handicaps"
        assert season_config.leaderboard_sheet_name == "Leaderboard"


TEST_SEASON_CONFIG_YAML_WRONG_EVENT_KEYS = """
name: SFSGT 2024
sheet_id: test_sheet_id
players_sheet_name: Player Handicaps
leaderboard_sheet_name: Leaderboard
events: {
  1: {
    event_name: Presidio,
    course_name: presidio,
    tee: blue,
    type: standard,
    scorecard_sheet_start_cell: B8,
    not_a_key: Foo Bar,
  },
  3: {
    event_name: Harding Park,
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


def test_event_names() -> None:
    with temp_season_config_file() as config_file:
        season_config = config.load_season_config_file(config_file)

        assert season_config.event_names() == {"Presidio", "Poppy Ridge", "Harding Park"}