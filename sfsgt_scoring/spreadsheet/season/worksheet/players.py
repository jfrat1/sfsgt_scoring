from typing import Any, NamedTuple

from gspread import utils
import pandas as pd

from sfsgt_scoring.spreadsheet import google
from sfsgt_scoring.spreadsheet.season.worksheet import dataframe


PLAYER_COLUMN_NAME = "Player"


class PlayersReadData(NamedTuple):
    player_handicaps: dict[str, "PlayerHandicaps"]


class PlayerHandicaps(NamedTuple):
    handicap_index_by_event: dict[str, float]


class PlayerWorksheetVerificationError(Exception):
    """Exception to be raised when an error is detected during verification of the players worksheet."""


class PlayersWorksheet:
    def __init__(self, worksheet: google.GoogleWorksheet, events: list[str]) -> None:
        self._worksheet = worksheet
        self._events = events

    def read(self) -> PlayersReadData:
        worksheet_data = self._get_worksheet_data()
        return self._generate_read_data(worksheet_data)

    def _get_worksheet_data(self) -> pd.DataFrame:
        worksheet_data_raw = self._worksheet.to_df()
        worksheet_data = self._process_raw_worksheet_data(worksheet_data_raw)

        self._check_worksheet_data(worksheet_data)

        return worksheet_data

    def _process_raw_worksheet_data(self, worksheet_data_raw: pd.DataFrame) -> pd.DataFrame:
        data_with_player_index = self._raise_player_column_to_index(worksheet_data_raw)
        data_numericised = dataframe.numericise_all_values(data_with_player_index)
        return data_numericised

    def _raise_player_column_to_index(self, worksheet_data: pd.DataFrame) -> pd.DataFrame:
        if PLAYER_COLUMN_NAME not in worksheet_data.columns:
            raise PlayerWorksheetVerificationError(
                f"The players worksheet must have a column named {PLAYER_COLUMN_NAME}"
            )
        return worksheet_data.set_index(keys=PLAYER_COLUMN_NAME, inplace=False)

    def _check_worksheet_data(self, worksheet_data: pd.DataFrame) -> None:
        self._check_column_headers(worksheet_data)
        self._check_data_values(worksheet_data)

    def _check_column_headers(self, worksheet_data: pd.DataFrame) -> None:
        column_headers = set(worksheet_data.columns)
        expected_headers = set(self._events)

        if column_headers != expected_headers:
            raise PlayerWorksheetVerificationError(
                "Players worksheet headers do not match expectations.\n"
                f"Headers: {column_headers}\nExpected headers: {expected_headers}"
            )

    def _check_data_values(self, worksheet_data: pd.DataFrame) -> None:
        for row_name, row in worksheet_data.iterrows():
            for col_name, value in row.items():
                self._check_data_value(value=value, row_name=row_name, col_name=col_name)

    def _check_data_value(self, value: Any, row_name: str, col_name: str) -> None:
        if not isinstance(value, (int, float)):
            raise PlayerWorksheetVerificationError(
                "Cell values in the players worksheet must be numeric values."
                f"The value at row: {row_name}, col: {col_name} is invalid. Found: {value}"
            )

    def _generate_read_data(self, worksheet_data: pd.DataFrame) -> PlayersReadData:
        player_handicaps = {
            player_name: self._generate_player_handicaps(player_row)
            for player_name, player_row in worksheet_data.iterrows()
        }
        return PlayersReadData(player_handicaps=player_handicaps)

    def _generate_player_handicaps(self, player_row: pd.Series) -> PlayerHandicaps:
        handicaps_by_event = {
            event_name: handicap_index for event_name, handicap_index in player_row.items()
        }
        return PlayerHandicaps(handicap_index_by_event=handicaps_by_event)
