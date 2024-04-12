from unittest import mock

import pandas as pd
import pytest
from pandas import testing as pd_testing

from sfsgt_scoring.spreadsheet.season.worksheet import players

TEST_EVENTS = {"Event A", "Event B"}

TEST_WORKSHEET_DATA_RAW = pd.DataFrame(
    data=[["Geoff", 12.5, 12.0], ["Bolt", 4, 4.3]],
    columns=["Player", "Event A", "Event B"],
)
TEST_WORKSHEET_DATA = TEST_WORKSHEET_DATA_RAW.set_index(keys="Player", inplace=False)

EXPECTED_TEST_READ_DATA = players.PlayersReadData(
    player_handicaps={
        "Geoff": players.HandicapIndexByEvent(
            data={"Event A": 12.5, "Event B": 12.0},
            events={"Event A", "Event B"},
        ),
        "Bolt": players.HandicapIndexByEvent(
            data={"Event A": 4.0, "Event B": 4.3},
            events={"Event A", "Event B"},
        ),
    }
)


def stub_google_worksheet(data: pd.DataFrame = TEST_WORKSHEET_DATA_RAW) -> mock.MagicMock:
    stub_worksheet = mock.MagicMock(spec=players.google.GoogleWorksheet)
    stub_worksheet.to_df.return_value = data

    return stub_worksheet


def create_test_players_worksheet() -> players.PlayersWorksheet:
    return players.PlayersWorksheet(worksheet=stub_google_worksheet(), events=TEST_EVENTS)


def test_read_nominal() -> None:
    players_worksheet = create_test_players_worksheet()

    assert players_worksheet.read() == EXPECTED_TEST_READ_DATA


def test_handicap_by_event_constructor() -> None:
    players.HandicapIndexByEvent(
        events={"foo", "bar"},
        data={"foo": 12.2, "bar": 14.2},
    )


def test_handicap_by_event_constructor_wrong_keys_raises_error() -> None:
    with pytest.raises(players.PlayerHandicapsVerificationError):
        players.HandicapIndexByEvent(
            events={"bar", "baz"},
            data={"foo": 12.2, "bar": 14.2},
        )


def test_read_with_string_numerics_in_raw_worksheet_data() -> None:
    test_data = TEST_WORKSHEET_DATA_RAW.copy()

    # Change data type to be generic object then convert all values to strings.
    test_data = test_data.astype(object)
    for (index, row) in test_data.iterrows():
        for (column, value) in row.items():
            test_data.loc[str(index), str(column)] = str(value)

    players_worksheet = players.PlayersWorksheet(
        worksheet=stub_google_worksheet(data=test_data),
        events=TEST_EVENTS,
    )

    assert players_worksheet.read() == EXPECTED_TEST_READ_DATA


def test_get_worksheet_data() -> None:
    players_worksheet = create_test_players_worksheet()

    pd_testing.assert_frame_equal(
        left=players_worksheet._get_worksheet_data(), right=TEST_WORKSHEET_DATA
    )


def test_raise_player_column_to_index() -> None:
    players_worksheet = create_test_players_worksheet()

    pd_testing.assert_frame_equal(
        left=players_worksheet._raise_player_column_to_index(TEST_WORKSHEET_DATA_RAW),
        right=TEST_WORKSHEET_DATA,
    )


def test_check_column_headers_passes() -> None:
    players_worksheet = create_test_players_worksheet()
    players_worksheet._check_column_headers(TEST_WORKSHEET_DATA)


def test_check_column_headers_missing_headers_raises_error() -> None:
    players_worksheet = create_test_players_worksheet()

    test_data = TEST_WORKSHEET_DATA.drop(labels="Event A", axis=1, inplace=False)

    with pytest.raises(players.PlayerWorksheetVerificationError):
        players_worksheet._check_column_headers(test_data)


def test_check_data_values_passes() -> None:
    players_worksheet = create_test_players_worksheet()
    players_worksheet._check_data_values(TEST_WORKSHEET_DATA)


def test_check_data_values_wrong_value_type_raises_error() -> None:
    players_worksheet = create_test_players_worksheet()

    test_data = TEST_WORKSHEET_DATA.copy()
    # Change type of 'Event A' column before writing a string to one of the values
    test_data["Event A"] = test_data["Event A"].astype(dtype=object)
    test_data.loc["Bolt", "Event A"] = "not a handicap index"

    with pytest.raises(players.PlayerWorksheetVerificationError):
        players_worksheet._check_data_values(test_data)


def test_generate_read_data() -> None:
    players_worksheet = create_test_players_worksheet()

    read_data = players_worksheet._generate_read_data(TEST_WORKSHEET_DATA)

    assert read_data == EXPECTED_TEST_READ_DATA


def test_players_read_data_player_names() -> None:
    players_read_data = EXPECTED_TEST_READ_DATA

    assert players_read_data.player_names() == {"Geoff", "Bolt"}
