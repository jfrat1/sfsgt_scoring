from typing import Generator, NamedTuple

import pytest
from unittest import mock

from .. import sheet
from ..worksheet import event, players

TEST_SHEET_CONFIG = sheet.SeasonSheetConfig(
    sheet_id="test_sheet_id",
    leaderboard_sheet_name="Leaderboard",
    players_sheet_name="Handicaps",
    events={
        "Presidio": sheet.SeasonSheetEventConfig(
            event_num=1,
            sheet_name="Presidio",
            scorecard_start_cell="B8",
        ),
        "Harding Park": sheet.SeasonSheetEventConfig(
            event_num=2,
            sheet_name="TPC Harding",
            scorecard_start_cell="B8",
        ),
    }
)

TEST_EVENTS = [
    "Presidio",
    "Harding Park",
]

TEST_PLAYERS = [
    "Stanton Turner",
    "John Fratello",
]

TEST_WORKSHEET_TITLES = [
    "Leaderboard",
    "Handicaps",
    "Presidio",
    "TPC Harding",
]

TEST_PLAYERS_READ_DATA = players.PlayersReadData(
    player_handicaps={
        "Stanton Turner": players.HandicapIndexByEvent(
            data={"Presidio": 12.0, "Harding Park": 12.2},
            events=["Presidio", "Harding Park"],
        ),
        "John Fratello": players.HandicapIndexByEvent(
            data={"Presidio": 15.8, "Harding Park": 15.4},
            events=["Presidio", "Harding Park"],
        ),
    }
)

TEST_PRESIDIO_EVENT_READ_DATA = event.EventReadData(
    player_scores={
        "Stanton Turner": event.HoleScores(
            scores={1: 5, 2: 4, 3: 5, 4: 6, 5: 5, 6: 6, 7: 4, 8: 4, 9: 5, 10: 6, 11: 6, 12: 5, 13: 4, 14: 4, 15: 4, 16: 4, 17: 4, 18: 5}  # noqa: E501
        ),
        "John Fratello": event.HoleScores(
            scores={1: 5, 2: 4, 3: 5, 4: 6, 5: 5, 6: 6, 7: 4, 8: 4, 9: 5, 10: 6, 11: 6, 12: 5, 13: 4, 14: 4, 15: 4, 16: 4, 17: 4, 18: 5}  # noqa: E501
        ),
    }
)

TEST_HARDING_PARK_EVENT_READ_DATA = event.EventReadData(
    player_scores={
        "Stanton Turner": event.HoleScores(
            scores={1: 5, 2: 4, 3: 5, 4: 6, 5: 5, 6: 6, 7: 4, 8: 4, 9: 5, 10: 6, 11: 6, 12: 5, 13: 4, 14: 4, 15: 4, 16: 4, 17: 4, 18: 5}  # noqa: E501
        ),
        "John Fratello": event.HoleScores(
            scores={1: 5, 2: 4, 3: 5, 4: 6, 5: 5, 6: 6, 7: 4, 8: 4, 9: 5, 10: 6, 11: 6, 12: 5, 13: 4, 14: 4, 15: 4, 16: 4, 17: 4, 18: 5}  # noqa: E501
        ),
    }
)


def configure_google_sheet_stub(stubbed_google_sheet_constructor: mock.MagicMock) -> None:
    stub_google_sheet = stubbed_google_sheet_constructor.return_value
    stub_google_sheet.worksheet_titles.return_value = TEST_WORKSHEET_TITLES


@pytest.fixture()
def stub_google_sheet_constructor() -> Generator[mock.MagicMock, None, None]:
    with mock.patch.object(sheet.google, "GoogleSheet", autospec=True) as stub:
        configure_google_sheet_stub(stub)
        yield stub


def configure_players_worksheet_stub(stubbed_players_worksheet_constructor: mock.MagicMock) -> None:
    stub_players_worksheet = stubbed_players_worksheet_constructor.return_value
    stub_players_worksheet.player_names.return_value = TEST_PLAYERS
    stub_players_worksheet.read.return_value = TEST_PLAYERS_READ_DATA


@pytest.fixture()
def stub_players_worksheet_constructor() -> Generator[mock.MagicMock, None, None]:
    with mock.patch.object(sheet.worksheet, "PlayersWorksheet", autospec=True) as stub:
        configure_players_worksheet_stub(stub)
        yield stub


@pytest.fixture()
def stub_leaderboard_worksheet_constructor() -> Generator[mock.MagicMock, None, None]:
    with mock.patch.object(sheet.worksheet, "LeaderboardWorksheet", autospec=True) as stub:
        yield stub


def configure_event_worksheet_stub(stubbed_event_worksheet_constructor: mock.MagicMock) -> None:
    stub_presidio_worksheet = mock.MagicMock(spec=event.EventWorksheet)
    stub_presidio_worksheet.read.return_value = TEST_PRESIDIO_EVENT_READ_DATA

    stub_harding_park_worsheet = mock.MagicMock(spec=event.EventWorksheet)
    stub_harding_park_worsheet.read.return_value = TEST_HARDING_PARK_EVENT_READ_DATA

    stubbed_event_worksheet_constructor.side_effect = [
        stub_presidio_worksheet,
        stub_harding_park_worsheet,
    ]


@pytest.fixture()
def stub_event_worksheet_constructor() -> Generator[mock.MagicMock, None, None]:
    with mock.patch.object(sheet.worksheet, "EventWorksheet", autospec=True) as stub:
        configure_event_worksheet_stub(stub)
        yield stub


class CollaboratorStubs(NamedTuple):
    google_sheet: mock.MagicMock
    players_worksheet: mock.MagicMock
    leaderboard_worksheet: mock.MagicMock
    event_worksheet: mock.MagicMock


@pytest.fixture()
def stubs(
    stub_google_sheet_constructor: mock.MagicMock,
    stub_players_worksheet_constructor: mock.MagicMock,
    stub_leaderboard_worksheet_constructor: mock.MagicMock,
    stub_event_worksheet_constructor: mock.MagicMock,
) -> Generator[CollaboratorStubs, None, None]:
    yield CollaboratorStubs(
        google_sheet=stub_google_sheet_constructor,
        players_worksheet=stub_players_worksheet_constructor,
        leaderboard_worksheet=stub_leaderboard_worksheet_constructor,
        event_worksheet=stub_event_worksheet_constructor,
    )


def verify_stub_calls_during_object_configuration(stubs: CollaboratorStubs) -> None:
    assert stubs.google_sheet.return_value.worksheet.call_args_list == [
        mock.call(worksheet_name="Handicaps"),
        mock.call(worksheet_name="Leaderboard"),
        mock.call(worksheet_name="Presidio"),
        mock.call(worksheet_name="TPC Harding"),
    ]

    # The same MagicMock object is returned for all calls to the google_sheet.worksheet()
    # method. These returned objects are passed along to the worksheet class constructors.
    shared_worksheet_stub = stubs.google_sheet.return_value.worksheet.return_value

    stubs.players_worksheet.assert_called_once_with(
        worksheet=shared_worksheet_stub,
        events=TEST_EVENTS,
    )

    stubs.leaderboard_worksheet.assert_called_once_with(
        worksheet=shared_worksheet_stub,
        players=TEST_PLAYERS,
        events={
            1: "Presidio",
            2: "Harding Park",
        }
    )

    assert stubs.event_worksheet.call_args_list == [
        mock.call(
            worksheet=shared_worksheet_stub,
            players=TEST_PLAYERS,
            scorecard_start_cell="B8",
        ),
        mock.call(
            worksheet=shared_worksheet_stub,
            players=TEST_PLAYERS,
            scorecard_start_cell="B8",
        ),
    ]


def test_sheet_construct_with_configuration(
    stubs: CollaboratorStubs,
) -> None:
    sheet.SeasonSheet(config=TEST_SHEET_CONFIG)

    verify_stub_calls_during_object_configuration(stubs)


def test_sheet_construct_in_unconfigured_state() -> None:
    sheet_ = sheet.SeasonSheet()

    assert not sheet_.is_configured
    assert sheet_.config is None
    assert sheet_.google_sheet is None


def test_sheet_configure_after_constructing_in_unconfigured_state(
    stubs: CollaboratorStubs,
) -> None:
    sheet_ = sheet.SeasonSheet()
    sheet_.configure(config=TEST_SHEET_CONFIG)

    assert sheet_.is_configured
    assert sheet_.config is not None
    assert sheet_.google_sheet is not None

    verify_stub_calls_during_object_configuration(stubs)


def test_sheet_constructor_wrong_worksheet_titles_raises_error(
    stubs: CollaboratorStubs,
) -> None:
    stubs.google_sheet.return_value.worksheet_titles.return_value = {"Wrong Title"}
    with pytest.raises(sheet.SeasonSheetVerificationError):
        sheet.SeasonSheet(config=TEST_SHEET_CONFIG)


def test_sheet_read(stubs: CollaboratorStubs) -> None:
    season_sheet = sheet.SeasonSheet(config=TEST_SHEET_CONFIG)

    read_data = season_sheet.read()

    assert read_data.players == TEST_PLAYERS_READ_DATA
    assert read_data.events["Presidio"] == TEST_PRESIDIO_EVENT_READ_DATA
    assert read_data.events["Harding Park"] == TEST_HARDING_PARK_EVENT_READ_DATA


def test_sheet_read_data_get_player_names() -> None:
    sheet_read_data = sheet.SeasonSheetReadData(
        players=TEST_PLAYERS_READ_DATA,
        events={
            "Presidio": TEST_PRESIDIO_EVENT_READ_DATA,
            "Harding Park": TEST_HARDING_PARK_EVENT_READ_DATA,
        }
    )
    assert sheet_read_data.player_names() == ["Stanton Turner", "John Fratello"]


def test_sheet_read_data_get_event_names() -> None:
    sheet_read_data = sheet.SeasonSheetReadData(
        players=TEST_PLAYERS_READ_DATA,
        events={
            "Presidio": TEST_PRESIDIO_EVENT_READ_DATA,
            "Harding Park": TEST_HARDING_PARK_EVENT_READ_DATA,
        }
    )
    assert sheet_read_data.event_names() == ["Presidio", "Harding Park"]


def test_sheet_read_in_unconfigured_state_raises_error() -> None:
    sheet_ = sheet.SeasonSheet()
    with pytest.raises(sheet.SeasonSheetNotConfiguredError):
        sheet_.read()
