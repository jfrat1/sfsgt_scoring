from sfsgt_scoring.spreadsheet import google as google_sheet
from .. import event


# This google sheet is a copy of the 2024 sheet with a small amount of fake
# data input for use in these tests.
TEST_GOOGLE_SHEET_ID = "1exNADFXKQphQmzluc7QLftqs-tI0CxqlWr2wDU3l6cQ"

# Names of real worksheets containing test data.
TEST_WORKSHEET_NAME = "Test Scorecard Write"

# All test worksheets have the same start cell
SCORECARD_START_CELL = "B8"

STANTON_WRITE_DATA = event.PlayerEventWriteData(
    front_9_strokes=36,
    back_9_strokes=38,
    gross_strokes=74,
    course_handicap=2,
    net_strokes=72,
    gross_rank=1,
    net_rank=1,
    gross_points=100,
    net_points=100,
    event_points=200,
    event_rank=1,
)

JOHN_WRITE_DATA = event.PlayerEventWriteData(
    front_9_strokes=40,
    back_9_strokes=42,
    gross_strokes=82,
    course_handicap=4,
    net_strokes=78,
    gross_rank=2,
    net_rank=3,
    gross_points=75,
    net_points=75,
    event_points=150,
    event_rank=3,
)

STEVE_WRITE_DATA = event.PlayerEventWriteData(
    front_9_strokes=38,
    back_9_strokes=40,
    gross_strokes=78,
    course_handicap=5,
    net_strokes=73,
    gross_rank=1,
    net_rank=1,
    gross_points=100,
    net_points=75,
    event_points=175,
    event_rank=2,
)

WRITE_DATA = event.EventWriteData(
    players={
        "Stanton Turner": STANTON_WRITE_DATA,
        "John Fratello": JOHN_WRITE_DATA,
        "Steve Harasym": STEVE_WRITE_DATA,
    },
    birdies=[],
    eagles=[],
    hole_scores_over_max=[],
)


PLAYER_NAMES = [
    "Stanton Turner",
    "John Fratello",
    "Steve Harasym",
]


def real_event_worksheet(worksheet_name: str = TEST_WORKSHEET_NAME) -> google_sheet.GoogleWorksheet:
    google_sheet_ = google_sheet.GoogleSheet(sheet_id=TEST_GOOGLE_SHEET_ID)
    return google_sheet_.worksheet(worksheet_name=worksheet_name)


def event_worksheet_class_instance(worksheet: google_sheet.GoogleWorksheet) -> event.EventWorksheet:
    event_worksheet = event.EventWorksheet(
        worksheet=worksheet,
        players=PLAYER_NAMES,
        scorecard_start_cell=SCORECARD_START_CELL,
    )
    event_worksheet._sorted_worksheet_player_names = PLAYER_NAMES.copy()

    return event_worksheet


def test_event_construct() -> None:
    worksheet = real_event_worksheet()
    event_sheet = event_worksheet_class_instance(worksheet)


def test_event_write() -> None:
    worksheet = real_event_worksheet()
    event_sheet = event_worksheet_class_instance(worksheet)

    event_sheet.write(write_data=WRITE_DATA)
