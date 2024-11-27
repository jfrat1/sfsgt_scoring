from typing import NamedTuple
from unittest import mock

import pytest

from sfsgt_scoring import course_database, season_config, season
from sfsgt_scoring.season import event as season_event
from sfsgt_scoring.spreadsheet import season as season_spreadsheet
from sfsgt_scoring.spreadsheet.season.worksheet import (
    players as players_worksheet,
    event as event_worksheet,
)

# System under test
from .. import season_runner

TEST_SEASON_CONFIG = season_config.SeasonConfig(
    name="test_season",
    sheet_id="test_sheet_id",
    players_sheet_name="Players",
    leaderboard_sheet_name="Leaderboard",
    finale_handicaps_sheet=season_config.FinaleSheetConfig(
        enabled=False,
        sheet_name="Finale - Corica",
    ),
    events={
        1: season_config.config.EventConfig(
            event_name="Standard Event",
            sheet_name="Standard Event Scorecard",
            course_name="standard_event_course",
            tee="white",
            type=season_config.config.EventType.STANDARD,
            scorecard_sheet_start_cell="A1",
        ),
        2: season_config.config.EventConfig(
            event_name="Major Event",
            sheet_name="Major Event Scorecard",
            course_name="major_event_course",
            tee="blue",
            type=season_config.config.EventType.MAJOR,
            scorecard_sheet_start_cell="B5",
        ),
    }
)


TEST_SEASON_SHEET_READ_DATA = season_spreadsheet.SeasonSheetReadData(
    players=players_worksheet.PlayersReadData(
        player_handicaps={
            "Stanton Turner": players_worksheet.HandicapIndexByEvent(
                data={"Standard Event": 12.0, "Major Event": 12.2},
                events=["Standard Event", "Major Event"],
            ),
            "John Fratello": players_worksheet.HandicapIndexByEvent(
                data={"Standard Event": 16.4, "Major Event": 16.2},
                events=["Standard Event", "Major Event"],
            ),
        },
    ),
    events={
        "Standard Event": event_worksheet.EventReadData(
            player_scores={
                "Stanton Turner": event_worksheet.HoleScores(
                    scores={1: 5, 2: 4, 3: 5, 4: 6, 5: 5, 6: 6, 7: 4, 8: 4, 9: 5, 10: 6, 11: 6, 12: 5, 13: 4, 14: 4, 15: 4, 16: 4, 17: 4, 18: 5}  # noqa: E501
                ),
                "John Fratello": event_worksheet.HoleScores(
                    scores={1: 5, 2: 7, 3: 6, 4: 3, 5: 5, 6: 6, 7: 3, 8: 5, 9: 6, 10: 7, 11: 6, 12: 4, 13: 3, 14: 5, 15: 3, 16: 4, 17: 5, 18: 6}  # noqa: E501
                ),
            }
        ),
        "Major Event": event_worksheet.EventReadData(
            player_scores={
                "Stanton Turner": event_worksheet.HoleScores(
                    scores={1: 5, 2: 4, 3: 5, 4: 6, 5: 5, 6: 6, 7: 4, 8: 4, 9: 5, 10: 6, 11: 6, 12: 5, 13: 4, 14: 4, 15: 4, 16: 4, 17: 4, 18: 5}  # noqa: E501
                ),
                "John Fratello": event_worksheet.IncompleteScore(),
            }
        ),
    }
)


class CourseDataForTests(NamedTuple):
    rating: float
    slope: int
    hole_pars: dict[int, int]


STANDARD_EVENT_COURSE_DATA = CourseDataForTests(
    rating=72.2,
    slope=130,
    hole_pars={
        1: 4,
        2: 4,
        3: 3,
        4: 5,
        5: 4,
        6: 4,
        7: 4,
        8: 3,
        9: 5,
        10: 5,
        11: 3,
        12: 5,
        13: 4,
        14: 4,
        15: 4,
        16: 4,
        17: 3,
        18: 4,
    },
)

MAJOR_EVENT_COURSE_DATA = CourseDataForTests(
    rating=72.8,
    slope=138,
    hole_pars={
        1: 4,
        2: 4,
        3: 3,
        4: 5,
        5: 4,
        6: 4,
        7: 4,
        8: 3,
        9: 5,
        10: 5,
        11: 3,
        12: 5,
        13: 4,
        14: 4,
        15: 4,
        16: 4,
        17: 3,
        18: 4,
    },
)

TEST_SEASON_INPUT = season.SeasonInput(
    events={
        "Standard Event": season_event.EventInput(
            course=season_event.CourseInput(
                name="standard_event_course",
                tee=season_event.CourseTeeData(
                    name="white",
                    rating=STANDARD_EVENT_COURSE_DATA.rating,
                    slope=STANDARD_EVENT_COURSE_DATA.slope,
                ),
                hole_pars=season_event.CourseHolePars(STANDARD_EVENT_COURSE_DATA.hole_pars),
            ),
            type=season_event.EventType.STANDARD,
            players={
                "Stanton Turner": season_event.EventPlayerInput(
                    handicap_index=12.0,
                    scorecard=season_event.Scorecard(
                        strokes_per_hole={1: 5, 2: 4, 3: 5, 4: 6, 5: 5, 6: 6, 7: 4, 8: 4, 9: 5, 10: 6, 11: 6, 12: 5, 13: 4, 14: 4, 15: 4, 16: 4, 17: 4, 18: 5},  # noqa: E501
                    ),
                ),
                "John Fratello": season_event.EventPlayerInput(
                    handicap_index=16.4,
                    scorecard=season_event.Scorecard(
                        strokes_per_hole={1: 5, 2: 7, 3: 6, 4: 3, 5: 5, 6: 6, 7: 3, 8: 5, 9: 6, 10: 7, 11: 6, 12: 4, 13: 3, 14: 5, 15: 3, 16: 4, 17: 5, 18: 6},  # noqa: E501
                    ),
                ),
            }
        ),
        "Major Event": season_event.EventInput(
            course=season_event.CourseInput(
                name="major_event_course",
                tee=season_event.CourseTeeData(
                    name="blue",
                    rating=MAJOR_EVENT_COURSE_DATA.rating,
                    slope=MAJOR_EVENT_COURSE_DATA.slope,
                ),
                hole_pars=season_event.CourseHolePars(MAJOR_EVENT_COURSE_DATA.hole_pars),
            ),
            type=season_event.EventType.MAJOR,
            players={
                "Stanton Turner": season_event.EventPlayerInput(
                    handicap_index=12.2,
                    scorecard=season_event.Scorecard(
                        strokes_per_hole={1: 5, 2: 4, 3: 5, 4: 6, 5: 5, 6: 6, 7: 4, 8: 4, 9: 5, 10: 6, 11: 6, 12: 5, 13: 4, 14: 4, 15: 4, 16: 4, 17: 4, 18: 5},  # noqa: E501
                    ),
                ),
                "John Fratello": season_event.EventPlayerInput(
                    handicap_index=16.2,
                    scorecard=season_event.IncompleteScorecard(),
                ),
            }
        )
    },
    player_names=["Stanton Turner", "John Fratello"],
)


class StubbedDependencies(NamedTuple):
    season_sheet: mock.MagicMock
    course_database: mock.MagicMock


def course_db_get_course(course_name: str) -> mock.MagicMock:
    stub_course = mock.MagicMock(spec=["name", "hole_par", "get_tee_info"])
    stub_course.get_tee_info.return_value.mock_add_spec = ["rating", "slope"]

    stub_course.name = course_name

    if course_name == "standard_event_course":
        stub_course.hole_pars = STANDARD_EVENT_COURSE_DATA.hole_pars
        stub_course.get_tee_info.return_value.rating = STANDARD_EVENT_COURSE_DATA.rating
        stub_course.get_tee_info.return_value.slope = STANDARD_EVENT_COURSE_DATA.slope

    elif course_name == "major_event_course":
        stub_course.hole_pars = MAJOR_EVENT_COURSE_DATA.hole_pars
        stub_course.get_tee_info.return_value.rating = MAJOR_EVENT_COURSE_DATA.rating
        stub_course.get_tee_info.return_value.slope = MAJOR_EVENT_COURSE_DATA.slope

    else:
        raise ValueError(f"Unknown course name: {course_name}")

    return stub_course


@pytest.fixture()
def stubbed_dependencies() -> StubbedDependencies:
    stub_sheet = mock.MagicMock(spec=season_spreadsheet.SeasonSheet)
    stub_sheet.read.return_value = TEST_SEASON_SHEET_READ_DATA

    stub_course_db = mock.MagicMock(spec=course_database.CourseDatabase)
    stub_course_db.get_course.side_effect = course_db_get_course

    return StubbedDependencies(
        season_sheet=stub_sheet,
        course_database=stub_course_db,
    )


def test_construct(stubbed_dependencies: StubbedDependencies) -> None:
    runner = season_runner.SeasonRunner(
        config=TEST_SEASON_CONFIG,
        sheet=stubbed_dependencies.season_sheet,
        course_db=stubbed_dependencies.course_database,
    )

    assert runner.config == TEST_SEASON_CONFIG
    assert runner.sheet is stubbed_dependencies.season_sheet
    assert runner.course_db is stubbed_dependencies.course_database

    stubbed_dependencies.season_sheet.configure.assert_called_once_with(
        season_spreadsheet.SeasonSheetConfig(
            sheet_id="test_sheet_id",
            players_sheet_name="Players",
            leaderboard_sheet_name="Leaderboard",
            events={
                "Standard Event": season_spreadsheet.SeasonSheetEventConfig(
                    event_num=1,
                    sheet_name="Standard Event Scorecard",
                    scorecard_start_cell="A1",
                ),
                "Major Event": season_spreadsheet.SeasonSheetEventConfig(
                    event_num=2,
                    sheet_name="Major Event Scorecard",
                    scorecard_start_cell="B5",
                ),
            },
            is_finale_enabled=False,
            finale_handicaps_sheet_name="Finale - Corica",
        )
    )


def test_read_spreadsheet_data(stubbed_dependencies: StubbedDependencies) -> None:
    runner = season_runner.SeasonRunner(
        config=TEST_SEASON_CONFIG,
        sheet=stubbed_dependencies.season_sheet,
        course_db=stubbed_dependencies.course_database,
    )
    assert runner._read_spreadsheet_data() == TEST_SEASON_SHEET_READ_DATA


def test_create_season(stubbed_dependencies: StubbedDependencies) -> None:
    runner = season_runner.SeasonRunner(
        config=TEST_SEASON_CONFIG,
        sheet=stubbed_dependencies.season_sheet,
        course_db=stubbed_dependencies.course_database,
    )

    season_ = runner._create_season(TEST_SEASON_SHEET_READ_DATA)
    assert season_._input == TEST_SEASON_INPUT


def test_create_season_input(stubbed_dependencies: StubbedDependencies) -> None:
    runner = season_runner.SeasonRunner(
        config=TEST_SEASON_CONFIG,
        sheet=stubbed_dependencies.season_sheet,
        course_db=stubbed_dependencies.course_database,
    )

    season_input = runner._season_input(spreadsheet_data=TEST_SEASON_SHEET_READ_DATA)
    assert season_input == TEST_SEASON_INPUT
