import pytest

from sfsgt_scoring.spreadsheet import google
from sfsgt_scoring.spreadsheet.season.worksheet import event

pytestmark = pytest.mark.integration


# This google sheet is a copy of the 2024 sheet with a small amount of fake
# data input for use in these tests.
TEST_GOOGLE_SHEET_ID = "1exNADFXKQphQmzluc7QLftqs-tI0CxqlWr2wDU3l6cQ"

# Names of real worksheets containing test data.
TEST_WORKSHEET_ALL_PLAYERS_HAVE_SCORES = "Test Scorecard (All players have scores)"
TEST_WORKSHEET_SOME_PLAYERS_MISSING_SCORES = "Test Scorecard (Some players empty)"
TEST_WORKSHEET_ALL_PLAYERS_MISSING_SCORES = "Test Scorecard (All players empty)"

# All test worksheets have the same start cell
SCORECARD_START_CELL = "B8"


def real_event_worksheet(worksheet_name: str = TEST_WORKSHEET_ALL_PLAYERS_HAVE_SCORES) -> google.GoogleWorksheet:
    google_sheet = google.GoogleSheet(sheet_id=TEST_GOOGLE_SHEET_ID)
    return google_sheet.worksheet(worksheet_name=worksheet_name)


def create_player_hole_scores(hole_scores: list[int]) -> event.HoleScores:
    assert len(hole_scores) == 18

    hole_numbers = range(1, 19)
    scores = {
        hole_num: hole_score
        for (hole_num, hole_score) in zip(hole_numbers, hole_scores)
    }
    return event.HoleScores(scores=scores)


def test_read_real_event_worksheet() -> None:
    event_ws = event.EventWorksheet(
        worksheet=real_event_worksheet(),
        players={"Stanton Turner", "John Fratello", "Steve Harasym"},
        scorecard_start_cell=SCORECARD_START_CELL,
    )
    read_data = event_ws.read()

    expected_read_data = event.EventReadData(
        player_scores={
            "Stanton Turner": create_player_hole_scores([5, 4, 5, 6, 5, 6, 4, 4, 5, 6, 6, 5, 4, 4, 4, 4, 4, 5]),
            "John Fratello": create_player_hole_scores([5, 7, 6, 3, 5, 6, 3, 5, 6, 7, 6, 4, 3, 5, 3, 4, 5, 6]),
            "Steve Harasym": create_player_hole_scores([4, 6, 4, 5, 5, 5, 4, 5, 5, 5, 5, 5, 4, 4, 5, 4, 5, 8]),
        }
    )

    assert read_data == expected_read_data
    assert event_ws._sorted_worksheet_player_names == ["Stanton Turner", "John Fratello", "Steve Harasym"]


def test_read_real_event_worksheet_some_players_missing_scores() -> None:
    event_ws = event.EventWorksheet(
        worksheet=real_event_worksheet(worksheet_name=TEST_WORKSHEET_SOME_PLAYERS_MISSING_SCORES),
        players={"Stanton Turner", "John Fratello", "Steve Harasym"},
        scorecard_start_cell=SCORECARD_START_CELL,
    )
    read_data = event_ws.read()

    expected_read_data = event.EventReadData(
        player_scores={
            "Stanton Turner": create_player_hole_scores([5, 4, 5, 6, 5, 6, 4, 4, 5, 6, 6, 5, 4, 4, 4, 4, 4, 5]),
            "John Fratello": event.IncompleteScore(),
            "Steve Harasym": event.IncompleteScore(),
        }
    )

    assert read_data == expected_read_data


def test_read_real_event_worksheet_all_players_missing_scores() -> None:
    event_ws = event.EventWorksheet(
        worksheet=real_event_worksheet(worksheet_name=TEST_WORKSHEET_ALL_PLAYERS_MISSING_SCORES),
        players={"Stanton Turner", "John Fratello", "Steve Harasym"},
        scorecard_start_cell=SCORECARD_START_CELL,
    )
    read_data = event_ws.read()

    expected_read_data = event.EventReadData(
        player_scores={
            "Stanton Turner": event.IncompleteScore(),
            "John Fratello": event.IncompleteScore(),
            "Steve Harasym": event.IncompleteScore(),
        }
    )

    assert read_data == expected_read_data
