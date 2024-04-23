import copy
from unittest import mock

import pandas as pd
import pytest
from pandas import testing as pd_testing

from sfsgt_scoring.spreadsheet.season.worksheet import event


TEST_PLAYERS = [
    "Stanton Turner",
    "John Fratello",
    "Steve Harasym",
]
TEST_SCORECARD_START_CELL = "B6"

# fmt: off
TEST_WORKSHEET_DATA_RAW = pd.DataFrame(
    data=[
        [
            "Stanton Turner", "5", "4", "5", "6", "5", "6", "4", "4", "5", "", "", "6", "6", "5", "4", "4", "4", "4", "4", "5",  # noqa(E501)
        ],
        [
            "John Fratello", "5", "7", "6", "3", "5", "6", "3", "5", "6", "", "", "7", "6", "4", "3", "5", "3", "4", "5", "6",  # noqa(E501)
        ],
        [
            "Steve Harasym", "4", "6", "4", "5", "5", "5", "4", "5", "5", "", "", "5", "5", "5", "4", "4", "5", "4", "5", "8",  # noqa(E501)
        ],
    ],
)
# fmt: on

TEST_WORKSHEET_DATA_PROCESSED = pd.DataFrame(
    data=[
        [5, 4, 5, 6, 5, 6, 4, 4, 5, 6, 6, 5, 4, 4, 4, 4, 4, 5],
        [5, 7, 6, 3, 5, 6, 3, 5, 6, 7, 6, 4, 3, 5, 3, 4, 5, 6],
        [4, 6, 4, 5, 5, 5, 4, 5, 5, 5, 5, 5, 4, 4, 5, 4, 5, 8],
    ],
    columns=[f"HOLE_{str(idx)}" for idx in range(1, 19)],
    index=pd.Index(data=TEST_PLAYERS, name="PLAYER"),
)


def create_player_hole_scores(hole_scores: list[int]) -> event.HoleScores:
    assert len(hole_scores) == 18

    hole_numbers = range(1, 19)
    data = {
        hole_num: hole_score
        for (hole_num, hole_score) in zip(hole_numbers, hole_scores)
    }
    return event.HoleScores(data)


EXPECTED_TEST_READ_DATA = event.EventReadData(
    player_scores={
        "Stanton Turner": create_player_hole_scores(
            [5, 4, 5, 6, 5, 6, 4, 4, 5, 6, 6, 5, 4, 4, 4, 4, 4, 5]
        ),
        "John Fratello": create_player_hole_scores(
            [5, 7, 6, 3, 5, 6, 3, 5, 6, 7, 6, 4, 3, 5, 3, 4, 5, 6]
        ),
        "Steve Harasym": create_player_hole_scores(
            [4, 6, 4, 5, 5, 5, 4, 5, 5, 5, 5, 5, 4, 4, 5, 4, 5, 8]
        ),
    }
)


def stub_google_worksheet(data: pd.DataFrame) -> mock.MagicMock:
    stub_worksheet = mock.MagicMock(spec=event.google_sheet.GoogleWorksheet)
    stub_worksheet.range_to_df.return_value = data

    return stub_worksheet


def create_test_event_worksheet(
    raw_worksheet_data: pd.DataFrame = TEST_WORKSHEET_DATA_RAW,
    players: list[str] = TEST_PLAYERS,
    scorecard_start_cell: str = TEST_SCORECARD_START_CELL,
) -> event.EventWorksheet:
    return event.EventWorksheet(
        worksheet=stub_google_worksheet(data=raw_worksheet_data),
        players=set(players),
        scorecard_start_cell=scorecard_start_cell,
    )


def test_player_hole_scores_constructor_all_integer_hole_scores() -> None:
    hole_scores = [5, 4, 5, 6, 5, 6, 4, 4, 5, 6, 6, 5, 4, 4, 4, 4, 4, 5]
    event.HoleScores(
        scores={hole_num: hole_score for hole_num, hole_score in zip(range(1, 19), hole_scores)}
    )


def test_player_hole_scores_constructor_missing_some_hole_scores_raises_error() -> None:
    hole_scores = [5, 4, 5, 6, 5, 6, 4, 4, None, 6, 6, 5, 4, 4, 4, 4, None, 5]
    with pytest.raises(event.PlayerHoleScoresVerificationError):
        event.HoleScores(
            scores={hole_num: hole_score for hole_num, hole_score in zip(range(1, 19), hole_scores)}  # type: ignore
        )


def test_player_hole_scores_constructor_missing_all_hole_scores_raises_error() -> None:
    hole_scores = [None] * 18
    with pytest.raises(event.PlayerHoleScoresVerificationError):
        event.HoleScores(
            scores={hole_num: hole_score for hole_num, hole_score in zip(range(1, 19), hole_scores)}  # type: ignore
        )


def test_player_hole_scores_constructor_missing_keys_raises_error() -> None:
    hole_scores = [5, 4, 5, 6, 5, 6, 4, 4, 5]
    with pytest.raises(event.PlayerHoleScoresVerificationError):
        event.HoleScores(
            scores={
                hole_num: hole_score
                for hole_num, hole_score in zip(range(1, len(hole_scores) + 1), hole_scores)
            }
        )


def test_player_hole_scores_constructor_string_keys_raises_error() -> None:
    hole_scores = [5, 4, 5, 6, 5, 6, 4, 4, 5, 6, 6, 5, 4, 4, 4, 4, 4, 5]
    with pytest.raises(event.PlayerHoleScoresVerificationError):
        event.HoleScores(
            scores={str(hole_num): hole_score for hole_num, hole_score in zip(range(1, 19), hole_scores)}  # type: ignore # noqa: E501
        )


def test_player_hols_scores_construct_string_value_raises_error() -> None:
    hole_scores = [5, 4, 5, 6, 5, 6, 4, 4, "5", 6, 6, 5, 4, 4, 4, 4, 4, 5]
    with pytest.raises(event.PlayerHoleScoresVerificationError):
        event.HoleScores(
            scores={hole_num: hole_score for hole_num, hole_score in zip(range(1, 19), hole_scores)}  # type: ignore
        )


def test_player_hols_scores_construct_empty_string_value_raises_error() -> None:
    hole_scores = [5, 4, 5, 6, 5, 6, 4, 4, "", 6, 6, 5, 4, 4, 4, 4, 4, 5]
    with pytest.raises(event.PlayerHoleScoresVerificationError):
        event.HoleScores(
            scores={hole_num: hole_score for hole_num, hole_score in zip(range(1, 19), hole_scores)}  # type: ignore
        )


def test_is_cell_a1_notation_true() -> None:
    event_worksheet = create_test_event_worksheet()
    assert event_worksheet._is_cell_a1_notation("B16")
    assert event_worksheet._is_cell_a1_notation("XX22")


def test_is_cell_a1_notation_false() -> None:
    event_worksheet = create_test_event_worksheet()
    assert not event_worksheet._is_cell_a1_notation("12")
    assert not event_worksheet._is_cell_a1_notation("B")


def test_read() -> None:
    event_worksheet = create_test_event_worksheet()
    read_data = event_worksheet.read()

    assert read_data == EXPECTED_TEST_READ_DATA


def test_get_worksheet_data() -> None:
    event_worksheet = create_test_event_worksheet()
    worksheet_data = event_worksheet._get_worksheet_data()

    pd_testing.assert_frame_equal(left=worksheet_data, right=TEST_WORKSHEET_DATA_PROCESSED)


def test_raw_worksheet_data() -> None:
    event_worksheet = create_test_event_worksheet()
    worksheet_data_raw = event_worksheet._raw_worksheet_data()
    pd_testing.assert_frame_equal(
        left=worksheet_data_raw, right=TEST_WORKSHEET_DATA_RAW
    )


def test_read_range() -> None:
    event_worksheet = create_test_event_worksheet(
        scorecard_start_cell="B8",
    )
    assert event_worksheet._read_range() == "B8:V10"


def test_read_range_end_cell() -> None:
    event_worksheet = create_test_event_worksheet(
        scorecard_start_cell="B8",
    )
    assert event_worksheet._read_range_end_cell() == "V10"


def test_read_range_row_offset() -> None:
    event_worksheet = create_test_event_worksheet()
    assert event_worksheet._read_range_row_offset() == 2


def test_num_players() -> None:
    event_worksheet = create_test_event_worksheet()
    assert event_worksheet._num_players() == 3


def test_read_range_col_offset() -> None:
    event_worksheet = create_test_event_worksheet()
    assert event_worksheet._read_range_col_offset() == 20


def test_process_raw_worksheet_data() -> None:
    event_worksheet = create_test_event_worksheet()
    worksheet_data_processed = event_worksheet._process_raw_worksheet_data(worksheet_data_raw=TEST_WORKSHEET_DATA_RAW)

    pd_testing.assert_frame_equal(left=worksheet_data_processed, right=TEST_WORKSHEET_DATA_PROCESSED)


def test_check_worksheet_data_nominal() -> None:
    event_worksheet = create_test_event_worksheet()
    event_worksheet._check_worksheet_data(worksheet_data=TEST_WORKSHEET_DATA_PROCESSED)


def test_check_worsheet_data_wrong_columns_raises_error() -> None:
    event_worksheet = create_test_event_worksheet()
    test_data = pd.DataFrame(
        data=[
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ],
        columns=["foo", "bar", "baz"],
        index=TEST_PLAYERS,
    )
    with pytest.raises(event.EventWorksheetVerificationError):
        event_worksheet._check_worksheet_data(worksheet_data=test_data)


def test_check_worksheet_data_missing_players_raises_error() -> None:
    event_worksheet = create_test_event_worksheet()

    test_data = TEST_WORKSHEET_DATA_PROCESSED.copy()
    test_data.drop(index=["Stanton Turner"], inplace=True)

    with pytest.raises(event.EventWorksheetVerificationError):
        event_worksheet._check_worksheet_data(worksheet_data=test_data)


def test_check_worksheet_data_non_numeric_and_non_empty_data_value_raises_error() -> None:
    event_worksheet = create_test_event_worksheet()

    test_data = TEST_WORKSHEET_DATA_PROCESSED.copy()
    test_data = test_data.astype(object)
    test_data.loc["Stanton Turner", "8"] = "foo bar"

    with pytest.raises(event.EventWorksheetVerificationError):
        event_worksheet._check_worksheet_data(worksheet_data=test_data)


def test_generate_read_data() -> None:
    event_worksheet = create_test_event_worksheet()

    read_data = event_worksheet._generate_read_data(worksheet_data=TEST_WORKSHEET_DATA_PROCESSED)
    assert read_data == EXPECTED_TEST_READ_DATA


def test_generate_read_data_with_empty_scores_for_one_player() -> None:
    event_worksheet = create_test_event_worksheet()

    test_data: pd.DataFrame = TEST_WORKSHEET_DATA_PROCESSED.copy()
    test_data = test_data.astype(object)
    test_data.loc["Stanton Turner", "HOLE_9"] = ""

    read_data = event_worksheet._generate_read_data(worksheet_data=test_data)

    expected_read_data: event.EventReadData = copy.deepcopy(EXPECTED_TEST_READ_DATA)
    expected_read_data.player_scores["Stanton Turner"] = event.IncompleteScore()

    assert read_data == expected_read_data


def test_generate_read_data_with_empty_scores_for_all_players() -> None:
    event_worksheet = create_test_event_worksheet()

    test_data: pd.DataFrame = TEST_WORKSHEET_DATA_PROCESSED.copy()
    test_data = test_data.astype(object)
    test_data.loc[:] = ""  # type: ignore

    read_data = event_worksheet._generate_read_data(worksheet_data=test_data)

    expected_read_data: event.EventReadData = copy.deepcopy(EXPECTED_TEST_READ_DATA)
    expected_read_data.player_scores["Stanton Turner"] = event.IncompleteScore()
    expected_read_data.player_scores["John Fratello"] = event.IncompleteScore()
    expected_read_data.player_scores["Steve Harasym"] = event.IncompleteScore()

    assert read_data == expected_read_data
