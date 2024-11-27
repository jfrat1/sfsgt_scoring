import enum
import functools
from typing import Any, NamedTuple

import pandas as pd

from sfsgt_scoring.spreadsheet import google
from sfsgt_scoring.spreadsheet.season.worksheet import dataframe


class EventHeaderNamesStyle(enum.Enum):
    UPPER_CASE = enum.auto()
    TITLE_CASE = enum.auto()
    LOWER_CASE = enum.auto()


# The row number where the headers of this table are stored.
HEADER_ROW_NUMBER = 2

# Header name for the player names column.
PLAYER_COLUMN_NAME = "GOLFER"

# Expected style for the event names in the spreadsheet.
EVENT_COLUMN_NAME_STYLE = EventHeaderNamesStyle.UPPER_CASE

FINALE_COLUMN_NAME = "FINALE"
UNUSED_TRAILING_COLUMN_NAMES = ["TRACKING METHOD"]

# Header names for columns are right of the handicap index values for each event.
TRAILING_COLUMN_NAMES = [FINALE_COLUMN_NAME] + UNUSED_TRAILING_COLUMN_NAMES


class PlayersReadData(NamedTuple):
    player_handicaps: dict[str, "HandicapIndexByEvent"]

    def player_names(self) -> list[str]:
        return list(self.player_handicaps.keys())


class PlayerHandicapsVerificationError(Exception):
    """Exception to be raised when player handicap data does not meet expectations."""


class HandicapIndexByEvent(dict[str, float]):
    def __init__(self, data: dict[str, float], events: list[str]):
        super().__init__(data)
        self._verify_keys(events)

    def _verify_keys(self, events: list[str]):
        keys = sorted(list(self.keys()))
        expected_keys = sorted(events + [FINALE_COLUMN_NAME])
        if keys != expected_keys:
            raise PlayerHandicapsVerificationError(
                "Player handicaps keys do not match events list."
                f"\nExpected: {events} \nFound: {keys}"
            )


class PlayerWorksheetVerificationError(Exception):
    """Exception to be raised when an error is detected during verification of the players worksheet."""


class PlayersWorksheet:
    def __init__(self, worksheet: google.GoogleWorksheet, events: list[str]) -> None:
        self._worksheet = worksheet
        self._events = events

    def read(self) -> PlayersReadData:
        worksheet_data = self._get_worksheet_data()
        return self._generate_read_data(worksheet_data)

    def player_names(self) -> list[str]:
        worksheet_data = self._get_worksheet_data()
        return list(worksheet_data.index)

    @functools.lru_cache()
    def _get_worksheet_data(self) -> pd.DataFrame:
        worksheet_data_raw = self._raw_worksheet_data()
        worksheet_data_processed = self._process_raw_worksheet_data(worksheet_data_raw)
        self._check_worksheet_data(worksheet_data_processed)

        return worksheet_data_processed

    def _raw_worksheet_data(self) -> pd.DataFrame:
        return self._worksheet.to_df(
            header_row=HEADER_ROW_NUMBER,
            expected_headers=self._expected_header_names(),
        )

    def _expected_header_names(self) -> list[str]:
        expected_headers = [PLAYER_COLUMN_NAME]
        expected_headers.extend(self._event_header_names())
        expected_headers.extend([FINALE_COLUMN_NAME])
        expected_headers.extend(UNUSED_TRAILING_COLUMN_NAMES)
        return expected_headers

    def _event_header_names(self) -> list[str]:
        return [self._event_column_name(event_name) for event_name in self._events]

    def _event_column_name(self, event_name: str) -> str:
        match EVENT_COLUMN_NAME_STYLE:
            case EventHeaderNamesStyle.UPPER_CASE:
                return event_name.upper()
            case EventHeaderNamesStyle.TITLE_CASE:
                return event_name.title()
            case EventHeaderNamesStyle.LOWER_CASE:
                return event_name.lower()

    def _process_raw_worksheet_data(self, worksheet_data_raw: pd.DataFrame) -> pd.DataFrame:
        worksheet_data_processed = worksheet_data_raw.copy()

        worksheet_data_processed = self._raise_player_column_to_index(worksheet_data_processed)
        worksheet_data_processed = self._drop_unused_columns(worksheet_data_processed)
        worksheet_data_processed = self._rename_event_columns_to_input_event_names(worksheet_data_processed)
        worksheet_data_processed = dataframe.numericise_all_values(worksheet_data_processed)

        return worksheet_data_processed

    def _raise_player_column_to_index(self, worksheet_data: pd.DataFrame) -> pd.DataFrame:
        if PLAYER_COLUMN_NAME not in worksheet_data.columns:
            raise PlayerWorksheetVerificationError(
                f"The players worksheet must have a column named {PLAYER_COLUMN_NAME}"
            )
        return worksheet_data.set_index(keys=PLAYER_COLUMN_NAME, inplace=False)

    def _drop_unused_columns(self, worksheet_data: pd.DataFrame) -> pd.DataFrame:
        worksheet_data_mod = worksheet_data.copy()

        worksheet_data_mod = self._drop_empty_columns(worksheet_data_mod)
        worksheet_data_mod = self._drop_trailing_columns(worksheet_data_mod)

        return worksheet_data_mod

    def _drop_empty_columns(self, worksheet_data: pd.DataFrame) -> pd.DataFrame:
        if "" in worksheet_data.columns:
            return worksheet_data.drop(labels=[""], axis="columns")

        return worksheet_data

    def _drop_trailing_columns(self, worksheet_data: pd.DataFrame) -> pd.DataFrame:
        return worksheet_data.drop(columns=UNUSED_TRAILING_COLUMN_NAMES)

    def _rename_event_columns_to_input_event_names(self, worksheet_data: pd.DataFrame) -> pd.DataFrame:
        return worksheet_data.rename(columns=self._event_column_rename_map())

    def _event_column_rename_map(self) -> dict[str, str]:
        events = self._events + [FINALE_COLUMN_NAME]
        return {
            self._event_column_name(event): event
            for event in events
        }

    def _check_worksheet_data(self, worksheet_data: pd.DataFrame) -> None:
        self._check_column_headers(worksheet_data)
        self._check_data_values(worksheet_data)

    def _check_column_headers(self, worksheet_data: pd.DataFrame) -> None:
        column_headers = list(worksheet_data.columns)
        expected_headers = list(self._events) + [FINALE_COLUMN_NAME]

        if column_headers != expected_headers:
            raise PlayerWorksheetVerificationError(
                "Players worksheet headers do not match expectations.\n"
                f"Headers: {column_headers}\nExpected headers: {expected_headers}"
            )

    def _check_data_values(self, worksheet_data: pd.DataFrame) -> None:
        for row_name, row in worksheet_data.iterrows():
            for col_name, value in row.items():
                self._check_data_value(value=value, row_name=str(row_name), col_name=str(col_name))

    def _check_data_value(self, value: Any, row_name: str, col_name: str) -> None:
        if not isinstance(value, (int, float)):
            raise PlayerWorksheetVerificationError(
                "Cell values in the players worksheet must be numeric values."
                f"The value at row: {row_name}, col: {col_name} is invalid. Found: {value}"
            )

    def _generate_read_data(self, worksheet_data: pd.DataFrame) -> PlayersReadData:
        player_handicaps = {
            str(player_name): self._generate_player_handicaps(player_row)
            for player_name, player_row in worksheet_data.iterrows()
        }
        return PlayersReadData(player_handicaps=player_handicaps)

    def _generate_player_handicaps(self, player_row: pd.Series) -> HandicapIndexByEvent:
        handicaps_by_event = {
            str(event_name): handicap_index for event_name, handicap_index in player_row.items()
        }
        return HandicapIndexByEvent(data=handicaps_by_event, events=self._events)
