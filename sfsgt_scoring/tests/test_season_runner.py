from typing import Generator, NamedTuple
from unittest import mock

import pytest

from sfsgt_scoring import season_config, season_runner
from sfsgt_scoring.spreadsheet.season.worksheet import players, event

TEST_SEASON_CONFIG = season_config.SeasonConfig(
    name="test_season",
    sheet_id="test_sheet_id",
    players_sheet_name="Players",
    leaderboard_sheet_name="Leaderboard",
    events={
        1: season_config.config.EventConfig(
            event_name="Standard Event",
            sheet_name="Standard Event Scorecard",
            course_name="course_a",
            tee="white",
            type=season_config.config.EventType.STANDARD,
            scorecard_sheet_start_cell="A1",
        ),
        2: season_config.config.EventConfig(
            event_name="Major Event",
            sheet_name="Major Event Scorecard",
            course_name="course_b",
            tee="blue",
            type=season_config.config.EventType.MAJOR,
            scorecard_sheet_start_cell="B5",
        ),
    }
)


TEST_SEASON_SHEET_READ_DATA = season_runner.spreadsheet.SeasonSheetReadData(
    players=players.PlayersReadData(
        player_handicaps={
            "Stanton Turner": players.HandicapIndexByEvent(
                data={"Standard Event": 12.0, "Major Event": 12.2},
                events={"Standard Event", "Major Event"},
            ),
            "John Fratello": players.HandicapIndexByEvent(
                data={"Standard Event": 16.4, "Major Event": 16.2},
                events={"Standard Event", "Major Event"},
            ),
        },
    ),
    events={
        "Standard Event": event.EventReadData(
            player_scores={
                "Stanton Turner": event.HoleScores(
                    {'1': 5, '2': 4, '3': 5, '4': 6, '5': 5, '6': 6, '7': 4, '8': 4, '9': 5, '10': 6, '11': 6, '12': 5, '13': 4, '14': 4, '15': 4, '16': 4, '17': 4, '18': 5}
                ),
                "John Fratello": event.HoleScores(
                    {'1': 5, '2': 7, '3': 6, '4': 3, '5': 5, '6': 6, '7': 3, '8': 5, '9': 6, '10': 7, '11': 6, '12': 4, '13': 3, '14': 5, '15': 3, '16': 4, '17': 5, '18': 6}
                )
            }
        ),
        "Major Event": event.EventReadData(
            player_scores={
                "Stanton Turner": event.HoleScores(
                    {'1': 5, '2': 4, '3': 5, '4': 6, '5': 5, '6': 6, '7': 4, '8': 4, '9': 5, '10': 6, '11': 6, '12': 5, '13': 4, '14': 4, '15': 4, '16': 4, '17': 4, '18': 5}
                ),
                "John Fratello": event.HoleScores(
                    {'1': 5, '2': 7, '3': 6, '4': 3, '5': 5, '6': 6, '7': 3, '8': 5, '9': 6, '10': 7, '11': 6, '12': 4, '13': 3, '14': 5, '15': 3, '16': 4, '17': 5, '18': 6}
                )
            }
        ),
    }
)


def configure_season_sheet_stub(stubbed_season_sheet_constructor: mock.MagicMock) -> None:
    stub_season_sheet = stubbed_season_sheet_constructor.return_value
    stub_season_sheet.read.return_value = TEST_SEASON_SHEET_READ_DATA


@pytest.fixture()
def stub_season_sheet_constructor() -> Generator[mock.MagicMock, None, None]:
    with mock.patch.object(season_runner.spreadsheet, "SeasonSheet", autospec=True) as stub:
        configure_season_sheet_stub(stub)
        yield stub


class CollaboratorStubs(NamedTuple):
    season_sheet: mock.MagicMock


@pytest.fixture()
def stubs(
    stub_season_sheet_constructor: mock.MagicMock
) -> CollaboratorStubs:
    return CollaboratorStubs(
        season_sheet=stub_season_sheet_constructor,
    )


def test_season_runner_construct(stubs: CollaboratorStubs) -> None:
    runner = season_runner.SeasonRunner(season_cfg=TEST_SEASON_CONFIG)

    assert runner.season_cfg == TEST_SEASON_CONFIG

    stubs.season_sheet.assert_called_once_with(
        config=season_runner.spreadsheet.SeasonSheetConfig(
            sheet_id="test_sheet_id",
            players_sheet_name="Players",
            leaderboard_sheet_name="Leaderboard",
            events={
                "Standard Event": season_runner.spreadsheet.SeasonSheetEventConfig(
                    sheet_name="Standard Event Scorecard",
                    scorecard_start_cell="A1",
                ),
                "Major Event": season_runner.spreadsheet.SeasonSheetEventConfig(
                    sheet_name="Major Event Scorecard",
                    scorecard_start_cell="B5",
                ),
            }
        )
    )


def test_season_runner_read_spreadsheet_data(stubs: CollaboratorStubs) -> None:
    runner = season_runner.SeasonRunner(season_cfg=TEST_SEASON_CONFIG)
    assert runner._read_spreadsheet_data() == TEST_SEASON_SHEET_READ_DATA