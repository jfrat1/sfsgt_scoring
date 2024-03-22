import pytest

from sfsgt_scoring.spreadsheet import google
from sfsgt_scoring.spreadsheet.season.worksheet import players

pytestmark = pytest.mark.integration

# This google sheet is a copy of the 2024 sheet with a small amount of fake
# data input for use in these tests.
TEST_GOOGLE_SHEET_ID = "1exNADFXKQphQmzluc7QLftqs-tI0CxqlWr2wDU3l6cQ"
# Name of the worksheet that has the player data
TEST_WORKSHEET_NAME = "Player Handicaps"


def real_players_worksheet() -> google.GoogleWorksheet:
    google_sheet = google.GoogleSheet(sheet_id=TEST_GOOGLE_SHEET_ID)
    return google_sheet.worksheet(worksheet_name=TEST_WORKSHEET_NAME)


def test_read_real_players_worksheet() -> None:
    player_ws = players.PlayersWorksheet(
        worksheet=real_players_worksheet(),
        events=["Presidio", "Poppy Ridge", "Harding Park"],
    )

    read_data = player_ws.read()
    expected_read_data = players.PlayersReadData(
        player_handicaps={
            "Stanton Turner": players.PlayerHandicaps(
                handicap_index_by_event={"Presidio": 14, "Poppy Ridge": 14, "Harding Park": 13.5}
            ),
            "John Fratello": players.PlayerHandicaps(
                handicap_index_by_event={"Presidio": 16, "Poppy Ridge": 16, "Harding Park": 16}
            ),
            "Steve Harasym": players.PlayerHandicaps(
                handicap_index_by_event={"Presidio": 8, "Poppy Ridge": 8, "Harding Park": 8.5}
            ),
        }
    )

    assert read_data == expected_read_data
