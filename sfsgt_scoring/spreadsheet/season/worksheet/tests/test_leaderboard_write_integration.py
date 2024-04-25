import copy
import pytest

from sfsgt_scoring.spreadsheet import google as google_sheet
from sfsgt_scoring.spreadsheet.season.worksheet import leaderboard

pytestmark = pytest.mark.integration

# This google sheet is a copy of the 2024 sheet with a small amount of fake
# data input for use in these tests.
TEST_GOOGLE_SHEET_ID = "1exNADFXKQphQmzluc7QLftqs-tI0CxqlWr2wDU3l6cQ"

# Names of real worksheets to write test data into
TEST_LEADERBOARD_SHEET = "Leaderboard Test Write"

PLAYERS = [
    "Stanton Turner",
    "John Fratello",
    "Steve Harasym",
]

EVENTS = {
    1: "Poppy Ridge",
    2: "Presidio",
    3: "Harding Park",
}

STANTON_WRITE_DATA = leaderboard.PlayerLeaderboardWriteData(
    player_name="Stanton Turner",
    season_points=250,
    season_rank=2,
    events_played=3,
    birdies=2,
    eagles=0,
    net_strokes_wins=0,
    wins=2,
    top_5s=1,
    top_10s=0,
    event_points={
        "Poppy Ridge": 100,
        "Presidio": 100,
        "Harding Park": 50,
    }
)

JOHN_WRITE_DATA = leaderboard.PlayerLeaderboardWriteData(
    player_name="John Fratello",
    season_points=200,
    season_rank=3,
    events_played=3,
    birdies=1,
    eagles=1,
    net_strokes_wins=2,
    wins=0,
    top_5s=2,
    top_10s=1,
    event_points={
        "Poppy Ridge": 50,
        "Presidio": 50,
        "Harding Park": 100,
    }
)

STEVE_WRITE_DATA = leaderboard.PlayerLeaderboardWriteData(
    player_name="Steve Harasym",
    season_points=350,
    season_rank=1,
    events_played=3,
    birdies=4,
    eagles=0,
    net_strokes_wins=0,
    wins=1,
    top_5s=2,
    top_10s=0,
    event_points={
        "Poppy Ridge": 100,
        "Presidio": 50,
        "Harding Park": 200,
    }
)

WRITE_DATA = leaderboard.LeaderboardWriteData(
    players=[
        STANTON_WRITE_DATA,
        JOHN_WRITE_DATA,
        STEVE_WRITE_DATA,
    ]
)


def real_event_worksheet(worksheet_name: str = TEST_LEADERBOARD_SHEET) -> google_sheet.GoogleWorksheet:
    google_sheet_ = google_sheet.GoogleSheet(sheet_id=TEST_GOOGLE_SHEET_ID)
    return google_sheet_.worksheet(worksheet_name=worksheet_name)


def test_construct_leaderboard_worksheet() -> None:
    worksheet = real_event_worksheet()

    leaderboard_ = leaderboard.LeaderboardWorksheet(
        worksheet=worksheet,
        players=PLAYERS,
        events=EVENTS,
    )


def test_write_data_sorted_by_rank() -> None:
    write_data = copy.deepcopy(WRITE_DATA)

    assert write_data.players_sorted_by_rank() == [
        STEVE_WRITE_DATA,
        STANTON_WRITE_DATA,
        JOHN_WRITE_DATA,
    ]


def test_leaderboard_last_player_row() -> None:
    worksheet = real_event_worksheet()

    leaderboard_ = leaderboard.LeaderboardWorksheet(
        worksheet=worksheet,
        players=PLAYERS,
        events=EVENTS,
    )

    assert leaderboard_._last_player_row() == 5


def test_leaderboard_write() -> None:
    worksheet = real_event_worksheet()

    leaderboard_ = leaderboard.LeaderboardWorksheet(
        worksheet=worksheet,
        players=PLAYERS,
        events=EVENTS,
    )

    leaderboard_.write(write_data=WRITE_DATA)
