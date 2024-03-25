from typing import Any, NamedTuple

import pandas as pd
from gspread import utils

from sfsgt_scoring.spreadsheet import google
from sfsgt_scoring.spreadsheet.season.worksheet import dataframe


EVENT_WORKSHEET_COLUMNS = [
    "Player",
    "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "Out", "Player Initial",
    "10", "11", "12", "13", "14", "15", "16", "17", "18",
    "In", "Total", "Course Handicap", "Net",
    "Gross Rank", "Net Rank", "Points", "Event Rank",
]

READ_DATA_FIRST_COLUMN = "Player"
READ_DATA_LAST_COLUMN = "18"
READ_DATA_FIRST_COL_INDEX = EVENT_WORKSHEET_COLUMNS.index(READ_DATA_FIRST_COLUMN)
READ_DATA_LAST_COL_INDEX = EVENT_WORKSHEET_COLUMNS.index(READ_DATA_LAST_COLUMN)


class EventReadData(NamedTuple):
    player_scores: dict[str, "HoleScores"]


class PlayerHoleScoresVerificationError(Exception):
    """Exception to be raised when a player hole score definition is invalid when being instantiated."""


class HoleScores(dict[str, int | None]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._verify_keys()
        self._verify_values()

    def _verify_keys(self) -> None:
        expected_keys = {str(hole) for hole in range(1, 19)}
        actual_keys = set(self.keys())
        if expected_keys != actual_keys:
            raise PlayerHoleScoresVerificationError(
                "Keys in the PlayerHoleScore dictionary must be strings containing hole numbers 1 through 18. "
                f"\nExpected: {expected_keys}\nFound: {actual_keys}"
            )

    def _verify_values(self) -> None:
        values = self.values()
        for value in values:
            is_value_none_or_int = value is None or isinstance(value, int)
            if not is_value_none_or_int:
                raise PlayerHoleScoresVerificationError(
                    f"Values in the PlayerHoleScore dictionary must be None or int type. Found: {self.values()}"
                )


class EventWriteData(NamedTuple):
    players: dict[str, "PlayerEventWriteData"]
    birdies: set["PlayerHole"]
    eagles: set["PlayerHole"]
    hole_scores_over_max: set["PlayerHole"]


class PlayerEventWriteData(NamedTuple):
    front_9_strokes: int
    back_9_strokes: int
    gross_strokes: int
    net_strokes: int
    gross_rank: int
    net_rank: int
    gross_points: float
    net_points: float
    event_points: float
    event_rank: int


class PlayerHole(NamedTuple):
    player: str
    hole: int



class InvalidCellDefinition(Exception):
    """Exception to be raised if a worksheet cell definition is invalid."""


class EventWorksheetVerificationError(Exception):
    """Exception to be raised when an error is detected during verification of the event worksheet."""


class EventWorksheet:
    def __init__(
        self,
        worksheet: google.GoogleWorksheet,
        players: set[str],
        scorecard_start_cell: str,
    ) -> None:
        self._worksheet = worksheet
        self._players = players
        self._scorecard_start_cell = scorecard_start_cell

        self._verify_scorecard_start_cell()

    def _verify_scorecard_start_cell(self) -> None:
        if not self._is_cell_a1_notation(self._scorecard_start_cell):
            raise InvalidCellDefinition(
                "Scorecard start cell definition is invalid. It must be in A1 notation. "
                f"Found: {self._scorecard_start_cell}"
            )

    def _is_cell_a1_notation(self, cell_name: str) -> bool:
        match = utils.CELL_ADDR_RE.match(string=cell_name)
        is_a1_notation = match is not None
        return is_a1_notation

    def read(self) -> EventReadData:
        worksheet_data = self._get_worksheet_data()
        return self._generate_read_data(worksheet_data)

    def _get_worksheet_data(self) -> pd.DataFrame:
        worksheet_data_raw = self._raw_worksheet_data()
        worksheet_data = self._process_raw_worksheet_data(worksheet_data_raw)

        self._check_worksheet_data(worksheet_data)
        return worksheet_data

    def _raw_worksheet_data(self) -> pd.DataFrame:
        return self._worksheet.range_to_df(range=self._read_range())

    def _read_range(self) -> str:
        return f"{self._scorecard_start_cell}:{self._read_range_end_cell()}"

    def _read_range_end_cell(self) -> str:
        (start_row, start_col) = utils.a1_to_rowcol(self._scorecard_start_cell)

        end_row = start_row + self._read_range_row_offset()
        end_col = start_col + self._read_range_col_offset()
        return utils.rowcol_to_a1(row=end_row, col=end_col)

    def _read_range_row_offset(self) -> int:
        return self._num_players() - 1

    def _num_players(self) -> int:
        return len(self._players)

    def _read_range_col_offset(self) -> int:
        first_col = READ_DATA_FIRST_COL_INDEX
        last_col = READ_DATA_LAST_COL_INDEX
        return last_col - first_col

    def _process_raw_worksheet_data(self, worksheet_data_raw: pd.DataFrame) -> pd.DataFrame:
        worksheet_data = worksheet_data_raw.copy()
        column_labels = EVENT_WORKSHEET_COLUMNS[READ_DATA_FIRST_COL_INDEX:READ_DATA_LAST_COL_INDEX+1]
        worksheet_data.columns = column_labels
        worksheet_data.drop(columns=["Out", "Player Initial"], inplace=True)
        worksheet_data.set_index(keys="Player", inplace=True)

        return dataframe.numericise_all_values(worksheet_data)

    def _check_worksheet_data(self, worksheet_data: pd.DataFrame) -> None:
        self._check_column_headers(worksheet_data)
        self._check_index_labels(worksheet_data)
        self._check_data_values(worksheet_data)

    def _check_column_headers(self, worksheet_data: pd.DataFrame) -> None:
        expected_columns = [str(hole_num) for hole_num in range(1, 19)]
        if not list(worksheet_data.columns) == expected_columns:
            raise EventWorksheetVerificationError(
                f"Worksheet data column labels do not match expectations."
                f"\nExpected: {expected_columns}, \nFound:{worksheet_data.columns}"
            )

    def _check_index_labels(self, worksheet_data: pd.DataFrame) -> None:
        expected_index = self._players
        index = set(worksheet_data.index)
        if not index == expected_index:
            raise EventWorksheetVerificationError(
                f"Worksheet data row labels do not match expectations."
                f"\nExpected: {expected_index}, \nFound:{index}"
            )

    def _check_data_values(self, worksheet_data: pd.DataFrame) -> None:
        for row_name, row in worksheet_data.iterrows():
            for col_name, value in row.items():
                self._check_data_value(value=value, row_name=row_name, col_name=col_name)

    def _check_data_value(self, value: Any, row_name: str, col_name: str) -> None:
        is_numeric = isinstance(value, (int, float))
        is_empty = value == ""
        is_numeric_or_empty = is_numeric or is_empty
        if not is_numeric_or_empty:
            raise EventWorksheetVerificationError(
                "Cell values in the event worksheet must be numeric values or empty."
                f"The value at row: {row_name}, col: {col_name} is invalid. Found: {value}"
            )

    def _generate_read_data(self, worksheet_data: pd.DataFrame) -> EventReadData:
        worksheet_data_modified = dataframe.replace_empty_strings_with_none(worksheet_data)

        player_scores = {
            player_name: HoleScores(scores_ser.to_dict())
            for (player_name, scores_ser) in worksheet_data_modified.iterrows()
        }

        return EventReadData(player_scores=player_scores)
