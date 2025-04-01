import copy
from unittest import mock

import pandas as pd
import pytest
from google_sheet import GoogleWorksheet, RangeValues, SortOrder, SortSpec
from pandas import testing as pd_testing
from season_common.scorecard import CompleteScorecard, IncompleteScorecard
from season_view.api.read_data import SeasonViewReadEvent
from season_view.api.write_data import (
    SeasonViewWriteEvent,
    SeasonViewWritePlayerCompleteEvent,
)
from season_view.google_sheet_view.worksheets import event
from season_view.google_sheet_view.worksheets.event import (
    EventWorksheet,
    EventWorksheetColumnOffsets,
    EventWorksheetError,
    EventWorksheetReader,
    EventWorksheetWriter,
)

STUB_EVENT = "Fake Event"
STUB_PLAYERS = [
    "Stanton Turner",
    "John Fratello",
    "Steve Harasym",
]
STUB_SCORECARD_START_CELL = "B6"

# fmt: off
STUB_WORKSHEET_DATA_RAW = pd.DataFrame(
    data=[
        [
            "Stanton Turner", "5", "4", "5", "6", "5", "6", "4", "4", "5", "", "", "6", "6", "5", "4", "4", "4", "4", "4", "5",  # noqa: E501
        ],
        [
            "John Fratello", "5", "7", "6", "3", "5", "6", "3", "5", "6", "", "", "7", "6", "4", "3", "5", "3", "4", "5", "6",  # noqa: E501
        ],
        [
            "Steve Harasym", "4", "6", "4", "5", "5", "5", "4", "5", "5", "", "", "5", "5", "5", "4", "4", "5", "4", "5", "8",  # noqa: E501
        ],
    ],
)
# fmt: on

STUB_WORKSHEET_DATA_PROCESSED = pd.DataFrame(
    data=[
        [5, 4, 5, 6, 5, 6, 4, 4, 5, 6, 6, 5, 4, 4, 4, 4, 4, 5],
        [5, 7, 6, 3, 5, 6, 3, 5, 6, 7, 6, 4, 3, 5, 3, 4, 5, 6],
        [4, 6, 4, 5, 5, 5, 4, 5, 5, 5, 5, 5, 4, 4, 5, 4, 5, 8],
    ],
    columns=[f"HOLE_{str(idx)}" for idx in range(1, 19)],
    index=pd.Index(data=STUB_PLAYERS, name="PLAYER"),
)

# The birdies and eagles don't match the actual hole scores above, but
# it doesn't matter for these specific tests
STUB_WORKSHEET_WRITE_DATA = SeasonViewWriteEvent(
    name=STUB_EVENT,
    players=[
        SeasonViewWritePlayerCompleteEvent(
            name="Stanton Turner",
            front_9_strokes=44,
            back_9_strokes=50,
            gross_strokes=94,
            course_handicap=14,
            net_strokes=80,
            gross_rank=2,
            net_rank=2,
            gross_points=45,
            net_points=45,
            event_points=90,
            event_rank=2,
            birdie_holes=[3, 16],
            eagle_holes=[],
            albatross_holes=[],
            over_max_holes=[],
        ),
        SeasonViewWritePlayerCompleteEvent(
            name="John Fratello",
            front_9_strokes=46,
            back_9_strokes=43,
            gross_strokes=89,
            course_handicap=16,
            net_strokes=73,
            gross_rank=1,
            net_rank=1,
            gross_points=50,
            net_points=50,
            event_points=100,
            event_rank=1,
            birdie_holes=[8],
            eagle_holes=[9],
            albatross_holes=[],
            over_max_holes=[],
        ),
        SeasonViewWritePlayerCompleteEvent(
            name="Steve Harasym",
            front_9_strokes=43,
            back_9_strokes=52,
            gross_strokes=95,
            course_handicap=7,
            net_strokes=88,
            gross_rank=3,
            net_rank=3,
            gross_points=37.5,
            net_points=37.5,
            event_points=75,
            event_rank=3,
            birdie_holes=[12],
            eagle_holes=[],
            albatross_holes=[],
            over_max_holes=[],
        ),
    ],
)


def create_player_scorecard(hole_scores: list[int]) -> CompleteScorecard:
    assert len(hole_scores) == 18

    hole_numbers = range(1, 19)
    data = {hole_num: hole_score for (hole_num, hole_score) in zip(hole_numbers, hole_scores)}
    return CompleteScorecard(data)


EXPECTED_SEASON_VIEW_READ_DATA = SeasonViewReadEvent(
    event_name=STUB_EVENT,
    player_scorecards={
        "Stanton Turner": create_player_scorecard([5, 4, 5, 6, 5, 6, 4, 4, 5, 6, 6, 5, 4, 4, 4, 4, 4, 5]),
        "John Fratello": create_player_scorecard([5, 7, 6, 3, 5, 6, 3, 5, 6, 7, 6, 4, 3, 5, 3, 4, 5, 6]),
        "Steve Harasym": create_player_scorecard([4, 6, 4, 5, 5, 5, 4, 5, 5, 5, 5, 5, 4, 4, 5, 4, 5, 8]),
    },
)
# Give this another name so that it can be used in 2 different contexts in the tests below
STUB_SEASON_VIEW_READ_DATA = EXPECTED_SEASON_VIEW_READ_DATA


def google_worksheet_double(data: pd.DataFrame = STUB_WORKSHEET_DATA_RAW) -> mock.MagicMock:
    stub_worksheet = mock.MagicMock(spec=event.google_sheet.GoogleWorksheet)
    stub_worksheet.range_to_df.return_value = data

    return stub_worksheet


# TODO: write some tests for the top-level event worksheet code
def create_event_worksheet() -> EventWorksheet:
    pass


def create_event_worksheet_reader(
    event_name: str = STUB_EVENT,
    google_worksheet: GoogleWorksheet | None = None,
    raw_worksheet_data: pd.DataFrame = STUB_WORKSHEET_DATA_RAW,
    scorecard_start_cell: str = STUB_SCORECARD_START_CELL,
    players: list[str] = STUB_PLAYERS,
) -> EventWorksheetReader:
    ws_controller = google_worksheet or google_worksheet_double(data=raw_worksheet_data)

    return EventWorksheetReader(
        event_name=event_name,
        worksheet_controller=ws_controller,
        scorecard_start_cell=scorecard_start_cell,
        players=players,
    )


def create_event_worksheet_writer(
    google_worksheet: GoogleWorksheet | None = None,
    data: SeasonViewWriteEvent = STUB_WORKSHEET_WRITE_DATA,
    scorecard_start_cell: str = STUB_SCORECARD_START_CELL,
    players_ordered_at_read_time: list[str] = STUB_PLAYERS,
) -> EventWorksheetWriter:
    ws_controller = google_worksheet or google_worksheet_double()
    return EventWorksheetWriter(
        data=data,
        worksheet_controller=ws_controller,
        scorecard_start_cell=scorecard_start_cell,
        players_ordered_at_read_time=players_ordered_at_read_time,
    )


def test_reader_read() -> None:
    reader = create_event_worksheet_reader()
    read_data = reader.read()

    assert read_data == EXPECTED_SEASON_VIEW_READ_DATA


def test_reader_raw_worksheet_data() -> None:
    reader = create_event_worksheet_reader()
    worksheet_data = reader._raw_worksheet_data()

    pd_testing.assert_frame_equal(left=worksheet_data, right=STUB_WORKSHEET_DATA_RAW)


def test_reader_processed_worksheet_data() -> None:
    reader = create_event_worksheet_reader()
    worksheet_data = reader._process_raw_worksheet_data(STUB_WORKSHEET_DATA_RAW)
    pd_testing.assert_frame_equal(left=worksheet_data, right=STUB_WORKSHEET_DATA_PROCESSED)


def test_reader_read_range() -> None:
    reader = create_event_worksheet_reader(
        scorecard_start_cell="B8",
    )
    assert reader._read_range() == "B8:V10"


def test_reader_read_range_end_cell() -> None:
    reader = create_event_worksheet_reader(
        scorecard_start_cell="B8",
    )
    assert reader._read_range_end_cell() == "V10"


def test_reader_read_range_row_offset() -> None:
    reader = create_event_worksheet_reader()
    assert reader._read_range_row_offset() == 2


def test_reader_num_players() -> None:
    reader = create_event_worksheet_reader()
    assert reader._num_players() == 3


def test_reader_read_range_col_offset() -> None:
    reader = create_event_worksheet_reader()
    assert reader._read_range_col_offset() == 20


def test_reader_check_worksheet_data_nominal() -> None:
    reader = create_event_worksheet_reader()
    reader._check_worksheet_data(worksheet_data=STUB_WORKSHEET_DATA_PROCESSED)


def test_reader_check_worsheet_data_wrong_columns_raises_error() -> None:
    reader = create_event_worksheet_reader()
    test_data = pd.DataFrame(
        data=[
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ],
        columns=["foo", "bar", "baz"],
        index=STUB_PLAYERS,
    )
    with pytest.raises(EventWorksheetError):
        reader._check_worksheet_data(worksheet_data=test_data)


# I don't think we check for this anymore
# def test_reader_check_worksheet_data_missing_players_raises_error() -> None:
#     reader = create_event_worksheet_reader()

#     test_data = STUB_WORKSHEET_DATA_PROCESSED.copy()
#     test_data.drop(index=["Stanton Turner"], inplace=True)

#     with pytest.raises(EventWorksheetError):
#         reader._check_worksheet_data(worksheet_data=test_data)


def test_reader_check_worksheet_data_non_numeric_and_non_empty_data_value_raises_error() -> None:
    reader = create_event_worksheet_reader()

    test_data = STUB_WORKSHEET_DATA_PROCESSED.copy()
    test_data = test_data.astype(object)
    test_data.loc["Stanton Turner", "8"] = "foo bar"

    with pytest.raises(EventWorksheetError):
        reader._check_worksheet_data(worksheet_data=test_data)


def test_reader_read_with_empty_scores_for_one_player() -> None:
    test_data: pd.DataFrame = STUB_WORKSHEET_DATA_RAW.copy()
    # test_data = test_data.astype(object)
    # Set the first player's 9th hole to an empty score
    test_data.iloc[0, 9] = ""

    stub_google_worksheet = google_worksheet_double(data=test_data)
    reader = create_event_worksheet_reader(google_worksheet=stub_google_worksheet)

    read_data = reader.read()

    expected_read_data: SeasonViewReadEvent = copy.deepcopy(EXPECTED_SEASON_VIEW_READ_DATA)
    expected_read_data._player_scorecards["Stanton Turner"] = IncompleteScorecard()

    assert read_data == expected_read_data


def test_reader_read_with_empty_scores_for_all_players() -> None:
    test_data: pd.DataFrame = STUB_WORKSHEET_DATA_RAW.copy()
    # test_data = test_data.astype(object)
    # This sets all of the hole scores to empty strings, but leaves the player names alone
    test_data.iloc[:, 1:] = ""

    stub_google_worksheet = google_worksheet_double(data=test_data)
    reader = create_event_worksheet_reader(google_worksheet=stub_google_worksheet)
    read_data = reader.read()

    expected_read_data: SeasonViewReadEvent = copy.deepcopy(EXPECTED_SEASON_VIEW_READ_DATA)
    expected_read_data._player_scorecards["Stanton Turner"] = IncompleteScorecard()
    expected_read_data._player_scorecards["John Fratello"] = IncompleteScorecard()
    expected_read_data._player_scorecards["Steve Harasym"] = IncompleteScorecard()

    assert read_data == expected_read_data


def test_writer_write() -> None:
    spy_google_worksheet = google_worksheet_double()
    spy_google_worksheet.column_range_values.return_value = STUB_PLAYERS

    writer = create_event_worksheet_writer(google_worksheet=spy_google_worksheet)

    writer.write()

    expected_write_ranges = [
        RangeValues(
            range="B6:B8",
            values=[
                ["Stanton Turner"],
                ["John Fratello"],
                ["Steve Harasym"],
            ],
        ),
        RangeValues(
            range="L6:L8",
            values=[
                [44],
                [46],
                [43],
            ],
        ),
        RangeValues(
            range="W6:AD8",
            values=[
                [50, 94, 14, 80, 2, 2, 90, 2],
                [43, 89, 16, 73, 1, 1, 100, 1],
                [52, 95, 7, 88, 3, 3, 75, 3],
            ],
        ),
    ]

    expected_sort_range = "B6:AD8"
    expected_sort_spec = SortSpec(
        column="AD",
        order=SortOrder.ASCENDING,
    )

    spy_google_worksheet.write_multiple_ranges.assert_called_once_with(expected_write_ranges)
    spy_google_worksheet.sort_range.assert_called_once_with(
        specs=[expected_sort_spec],
        range_name=expected_sort_range,
    )

    # TODO: This is a work in progress and shouldn't be called yet
    spy_google_worksheet.format_multiple_ranges.assert_not_called()


def test_writer_player_names_write_range() -> None:
    writer = create_event_worksheet_writer()

    expected_range = RangeValues(
        range="B6:B8",
        values=[
            ["Stanton Turner"],
            ["John Fratello"],
            ["Steve Harasym"],
        ],
    )

    assert writer._player_names_write_range() == expected_range


def test_writer_front_nine_write_range() -> None:
    writer = create_event_worksheet_writer()

    expected_range = RangeValues(
        range="L6:L8",
        values=[
            [44],
            [46],
            [43],
        ],
    )

    assert writer._front_nine_write_range(STUB_WORKSHEET_WRITE_DATA) == expected_range


def test_writer_back_nine_and_event_reults_write_range() -> None:
    writer = create_event_worksheet_writer()

    expected_range = RangeValues(
        range="W6:AD8",
        values=[
            [50, 94, 14, 80, 2, 2, 90, 2],
            [43, 89, 16, 73, 1, 1, 100, 1],
            [52, 95, 7, 88, 3, 3, 75, 3],
        ],
    )

    actual_range = writer._back_nine_and_event_results_write_range(STUB_WORKSHEET_WRITE_DATA)
    assert actual_range == expected_range


def test_writer_range_for_columns_nominal() -> None:
    writer = create_event_worksheet_writer()

    start_col = EventWorksheetColumnOffsets.FRONT_NINE_STROKES
    end_col = EventWorksheetColumnOffsets.PLAYER_INITIAL
    expected_range = "L6:M8"

    assert (
        writer._range_for_columns(
            start_col_offset=start_col,
            end_col_offset=end_col,
        )
        == expected_range
    )


def test_writer_range_for_columns_single_colum() -> None:
    writer = create_event_worksheet_writer()

    start_col = EventWorksheetColumnOffsets.FRONT_NINE_STROKES
    end_col = EventWorksheetColumnOffsets.FRONT_NINE_STROKES
    expected_range = "L6:L8"

    assert (
        writer._range_for_columns(
            start_col_offset=start_col,
            end_col_offset=end_col,
        )
        == expected_range
    )


# TODO: it looks like the writer might not do any sorting or formatting just yet
# def test_sort_scorecard_by_player_event_rank() -> None:
#     writer = create_event_worksheet_writer()

#     writer._sort_scorecard_by_player_event_rank()

#     expected_sort_range = "B6:AD8"
#     expected_sort_spec = event.google_sheet.SortSpec(
#         column="AD",
#         order=event.google_sheet.SortOrder.ASCENDING,
#     )

#     # Extract mocked google worksheet from event_worksheet class
#     google_worksheet_mock: mock.MagicMock = event_worksheet._worksheet  # type: ignore

#     google_worksheet_mock.sort_range.assert_called_once_with(
#         specs=[expected_sort_spec],
#         range_name=expected_sort_range,
#     )


# def test_set_hole_cells_to_standard_backrgound() -> None:
#     event_worksheet = create_test_event_worksheet()

#     event_worksheet._set_hole_cells_to_standard_background()

#     expected_cell_format = google_sheet.CellFormat(
#         # This test value is sensitive to changes in the source configured
#         # standard background color.
#         backgroundColor=google_sheet.ColorRgb(
#             red=252,
#             green=245,
#             blue=243,
#         )
#     )

#     # Extract mocked google worksheet from event_worksheet class
#     google_worksheet_mock: mock.MagicMock = event_worksheet._worksheet  # type: ignore
#     google_worksheet_mock.format_multiple_ranges.assert_called_once_with(
#         range_formats=[
#             google_sheet.RangeFormat(range="C6:K8", format=expected_cell_format),
#             google_sheet.RangeFormat(range="N6:V8", format=expected_cell_format),
#         ]
#     )


# def test_set_birdie_hole_cells_background() -> None:
#     event_worksheet = create_test_event_worksheet()
#     event_worksheet._set_birdie_hole_cells_background(
#         write_data=STUB_WORKSHEET_WRITE_DATA,
#         sorted_player_rows={
#             "John Fratello": 6,
#             "Stanton Turner": 7,
#             "Steve Harasym": 8,
#         },
#     )

#     expected_cell_format = google_sheet.CellFormat(
#         # This test value is sensitive to changes in the source configured
#         # standard background color.
#         backgroundColor=google_sheet.ColorRgb(
#             red=217,
#             green=234,
#             blue=211,
#         )
#     )

#     # Extract mocked google worksheet from event_worksheet class
#     google_worksheet_mock: mock.MagicMock = event_worksheet._worksheet  # type: ignore
#     google_worksheet_mock.format_multiple_ranges.assert_called_once_with(
#         range_formats=[
#             google_sheet.RangeFormat(range="E7", format=expected_cell_format),  # Stanton hole 3
#             google_sheet.RangeFormat(range="T7", format=expected_cell_format),  # Stanton hole 16
#             google_sheet.RangeFormat(range="J6", format=expected_cell_format),  # John hole 8
#             google_sheet.RangeFormat(range="P8", format=expected_cell_format),  # Steve hole 12
#         ]
#     )


# def test_set_eagle_hole_cells_background() -> None:
#     event_worksheet = create_test_event_worksheet()
#     event_worksheet._set_eagle_hole_cells_background(
#         write_data=STUB_WORKSHEET_WRITE_DATA,
#         sorted_player_rows={
#             "John Fratello": 6,
#             "Stanton Turner": 7,
#             "Steve Harasym": 8,
#         },
#     )

#     expected_cell_format = google_sheet.CellFormat(
#         # This test value is sensitive to changes in the source configured
#         # standard background color.
#         backgroundColor=google_sheet.ColorRgb(
#             red=255,
#             green=187,
#             blue=137,
#         )
#     )

#     # Extract mocked google worksheet from event_worksheet class
#     google_worksheet_mock: mock.MagicMock = event_worksheet._worksheet  # type: ignore
#     google_worksheet_mock.format_multiple_ranges.assert_called_once_with(
#         range_formats=[
#             google_sheet.RangeFormat(range="K6", format=expected_cell_format),  # John hole 9
#         ]
#     )


# def test_player_name_row_map() -> None:
#     event_worksheet = create_test_event_worksheet()

#     # Extract mocked google worksheet from event_worksheet class
#     google_worksheet_mock: mock.MagicMock = event_worksheet._worksheet  # type: ignore
#     google_worksheet_mock.column_range_values.return_value = [
#         "John Fratello",
#         "Stanton Turner",
#         "Steve Harasym",
#     ]

#     player_names_map = event_worksheet._player_name_row_map()
#     assert player_names_map == {
#         "John Fratello": 6,
#         "Stanton Turner": 7,
#         "Steve Harasym": 8,
#     }
