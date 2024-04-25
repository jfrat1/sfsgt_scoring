import abc
import enum
from typing import Any, NamedTuple

import pandas as pd
from gspread import utils as gspread_utils

from sfsgt_scoring.spreadsheet import google as google_sheet
from sfsgt_scoring.spreadsheet import sheet_utils
from sfsgt_scoring.spreadsheet.season.worksheet import dataframe


class EventWorksheetColumnOffsets(enum.Enum):
    PLAYER = 0
    HOLE_1 = 1
    HOLE_2 = 2
    HOLE_3 = 3
    HOLE_4 = 4
    HOLE_5 = 5
    HOLE_6 = 6
    HOLE_7 = 7
    HOLE_8 = 8
    HOLE_9 = 9
    FRONT_NINE_STROKES = 10
    PLAYER_INITIAL = 11
    HOLE_10 = 12
    HOLE_11 = 13
    HOLE_12 = 14
    HOLE_13 = 15
    HOLE_14 = 16
    HOLE_15 = 17
    HOLE_16 = 18
    HOLE_17 = 19
    HOLE_18 = 20
    BACK_NINE_STROKES = 21
    GROSS_STROKES = 22
    COURSE_HANDICAP = 23
    NET_STROKES = 24
    GROSS_RANK = 25
    NET_RANK = 26
    EVENT_POINTS = 27
    EVENT_RANK = 28


EVENT_WORKSHEET_COLUMN_NAMES = [
    e.name for e in EventWorksheetColumnOffsets
]

READ_DATA_FIRST_COLUMN = "PLAYER"
READ_DATA_LAST_COLUMN = "HOLE_18"
READ_DATA_FIRST_COL_INDEX = EVENT_WORKSHEET_COLUMN_NAMES.index(READ_DATA_FIRST_COLUMN)
READ_DATA_LAST_COL_INDEX = EVENT_WORKSHEET_COLUMN_NAMES.index(READ_DATA_LAST_COLUMN)


class EventReadData(NamedTuple):
    player_scores: dict[str, "IHoleScores"]


class PlayerHoleScoresVerificationError(Exception):
    """Exception to be raised when a player hole score definition is invalid when being instantiated."""


class IHoleScores(abc.ABC):
    @abc.abstractmethod
    def scores(self) -> dict[int, int]: pass


class IncompleteScore(IHoleScores):
    def __new__(cls):
        # Implement the singleton pattern for this class because there may be many
        # instances of it and they are stateless/identical.
        if not hasattr(cls, 'instance'):
            cls.instance = super(IncompleteScore, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        pass

    def scores(self) -> dict[int, int]:
        return {}


class HoleScores(IHoleScores):
    def __init__(self, scores: dict[int, int]) -> None:
        self._scores = scores
        self._verify_keys()
        self._verify_values()

    def _verify_keys(self) -> None:
        expected_keys = [hole for hole in range(1, 19)]
        actual_keys = list(self._scores.keys())
        if expected_keys != actual_keys:
            raise PlayerHoleScoresVerificationError(
                "Keys in the HoleScores dictionary must be integers containing hole numbers 1 through 18. "
                f"\nExpected: {expected_keys}\nFound: {actual_keys}"
            )

    def _verify_values(self) -> None:
        values = self._scores.values()
        are_all_values_int_type = all(isinstance(value, int) for value in values)

        if not are_all_values_int_type:
            raise PlayerHoleScoresVerificationError(
                f"Values in the HoleScores dictionary must int type. Found: {values}"
            )

    def scores(self) -> dict[int, int]:
        return self._scores

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, HoleScores):
            return NotImplemented

        else:
            return self._scores == other._scores


class EventWriteData(NamedTuple):
    players: dict[str, "PlayerEventWriteData"]
    birdies: list["PlayerHole"]
    eagles: list["PlayerHole"]
    hole_scores_over_max: list["PlayerHole"]


class PlayerEventWriteData(NamedTuple):
    front_9_strokes: int
    back_9_strokes: int
    gross_strokes: int
    course_handicap: int
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


class EventWorksheetWriteError(Exception):
    """Exception to be raised when an error is encountered while writing to the worksheet."""


class EventWorksheet:
    def __init__(
        self,
        worksheet: google_sheet.GoogleWorksheet,
        players: list[str],
        scorecard_start_cell: str,
    ) -> None:
        self._worksheet = worksheet
        self._players = players
        self._scorecard_start_cell = scorecard_start_cell
        self._sorted_worksheet_player_names: list[str] = []  # This will be set when reading from the sheet

        self._verify_scorecard_start_cell()

    def _verify_scorecard_start_cell(self) -> None:
        if not self._is_cell_a1_notation(self._scorecard_start_cell):
            raise InvalidCellDefinition(
                "Scorecard start cell definition is invalid. It must be in A1 notation. "
                f"Found: {self._scorecard_start_cell}"
            )

    def _is_cell_a1_notation(self, cell_name: str) -> bool:
        return sheet_utils.is_cell_a1_notation(cell_name)

    def read(self) -> EventReadData:
        worksheet_data = self._get_worksheet_data()
        return self._generate_read_data(worksheet_data)

    def _get_worksheet_data(self) -> pd.DataFrame:
        worksheet_data_raw = self._raw_worksheet_data()
        worksheet_data = self._process_raw_worksheet_data(worksheet_data_raw)
        self._sorted_worksheet_player_names = list(worksheet_data.index)

        self._check_worksheet_data(worksheet_data)
        return worksheet_data

    def _raw_worksheet_data(self) -> pd.DataFrame:
        return self._worksheet.range_to_df(range=self._read_range())

    def _read_range(self) -> str:
        return f"{self._scorecard_start_cell}:{self._read_range_end_cell()}"

    def _read_range_end_cell(self) -> str:
        (start_row, start_col) = gspread_utils.a1_to_rowcol(self._scorecard_start_cell)

        end_row = start_row + self._read_range_row_offset()
        end_col = start_col + self._read_range_col_offset()
        return gspread_utils.rowcol_to_a1(row=end_row, col=end_col)

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
        column_labels = EVENT_WORKSHEET_COLUMN_NAMES[READ_DATA_FIRST_COL_INDEX:READ_DATA_LAST_COL_INDEX+1]
        worksheet_data.columns = pd.Index(column_labels)
        worksheet_data.drop(columns=["FRONT_NINE_STROKES", "PLAYER_INITIAL"], inplace=True)
        worksheet_data.set_index(keys="PLAYER", inplace=True)

        return dataframe.numericise_all_values(worksheet_data)

    def _check_worksheet_data(self, worksheet_data: pd.DataFrame) -> None:
        self._check_column_headers(worksheet_data)
        self._check_index_labels(worksheet_data)
        self._check_data_values(worksheet_data)

    def _check_column_headers(self, worksheet_data: pd.DataFrame) -> None:
        expected_columns = [f"HOLE_{str(hole_num)}" for hole_num in range(1, 19)]
        if not list(worksheet_data.columns) == expected_columns:
            raise EventWorksheetVerificationError(
                f"Worksheet data column labels do not match expectations."
                f"\nExpected: {expected_columns}, \nFound:{worksheet_data.columns}"
            )

    def _check_index_labels(self, worksheet_data: pd.DataFrame) -> None:
        expected_index = sorted(self._players)
        index = sorted(list(worksheet_data.index))
        if not index == expected_index:
            raise EventWorksheetVerificationError(
                f"Worksheet data row labels do not match expectations."
                f"\nExpected: {expected_index}, \nFound:{index}"
            )

    def _check_data_values(self, worksheet_data: pd.DataFrame) -> None:
        for row_name, row in worksheet_data.iterrows():
            for col_name, value in row.items():
                self._check_data_value(value=value, row_name=str(row_name), col_name=str(col_name))

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
            str(player_name): self._generate_hole_scores(scores_ser)
            for (player_name, scores_ser) in worksheet_data_modified.iterrows()
        }
        return EventReadData(player_scores=player_scores)

    def _generate_hole_scores(self, scores_ser: pd.Series) -> IHoleScores:
        if scores_ser.isna().any():
            return IncompleteScore()
        else:
            scores_dict_raw = scores_ser.to_dict()
            scores_dict = {
                int(hole_num.replace("HOLE_", "")): hole_score
                for hole_num, hole_score in scores_dict_raw.items()
            }
            return HoleScores(scores=scores_dict)

    def write(self, write_data: EventWriteData) -> None:
        if not self._sorted_worksheet_player_names:
            raise EventWorksheetWriteError(
                "An unexpected error was encountered while writing. This suggests that the event "
                "worksheet was not read before being written to. Double check usage of this object "
                "to ensure that data is read before being written."
            )

        first_write_range = self._front_nine_write_range(write_data)
        second_write_range = self._back_nine_and_event_results_range(write_data)
        write_ranges = [first_write_range, second_write_range]

        self._worksheet.write_multiple_ranges(write_ranges)
        self._sort_scorecard_by_player_event_rank()

    def _front_nine_write_range(self, write_data: EventWriteData) -> google_sheet.RangeValues:
        range_name = self._range_for_columns(
            start_col_offset=EventWorksheetColumnOffsets.FRONT_NINE_STROKES,
            end_col_offset=EventWorksheetColumnOffsets.FRONT_NINE_STROKES,
        )

        values: list[list[google_sheet.CellValueType]] = []
        for player_name in self._sorted_worksheet_player_names:
            player_data = write_data.players[player_name]

            value: list[google_sheet.CellValueType] = [
                player_data.front_9_strokes,
            ]
            values.append(value)

        return google_sheet.RangeValues(
            range=range_name,
            values=values,
        )

    def _back_nine_and_event_results_range(self, write_data: EventWriteData) -> google_sheet.RangeValues:
        range_name = self._range_for_columns(
            start_col_offset=EventWorksheetColumnOffsets.BACK_NINE_STROKES,
            end_col_offset=EventWorksheetColumnOffsets.EVENT_RANK,
        )

        values: list[list[google_sheet.CellValueType]] = []
        for player_name in self._sorted_worksheet_player_names:
            player_data = write_data.players[player_name]

            value: list[google_sheet.CellValueType] = [
                player_data.back_9_strokes,
                player_data.gross_strokes,
                player_data.course_handicap,
                player_data.net_strokes,
                player_data.gross_rank,
                player_data.net_rank,
                player_data.event_points,
                player_data.event_rank,
            ]
            values.append(value)

        return google_sheet.RangeValues(
            range=range_name,
            values=values,
        )

    def _range_for_columns(
        self,
        start_col_offset: EventWorksheetColumnOffsets,
        end_col_offset: EventWorksheetColumnOffsets,
    ) -> str:
        (first_player_row, _) = self._first_player_row_col()

        start_row = first_player_row
        end_row = first_player_row + self._num_players() - 1

        start_col = self._column_letter_for_offset(start_col_offset)
        end_col = self._column_letter_for_offset(end_col_offset)

        return f"{start_col}{start_row}:{end_col}{end_row}"

    def _first_player_row_col(self) -> tuple[int, int]:
        return gspread_utils.a1_to_rowcol(self._scorecard_start_cell)

    def _column_letter_for_offset(self, col_offset: EventWorksheetColumnOffsets) -> str:
        (_, first_player_col) = self._first_player_row_col()
        col_idx = first_player_col + col_offset.value
        return sheet_utils.column_letter_for_idx(col_idx)

    def _sort_scorecard_by_player_event_rank(self) -> None:
        sort_range = self._range_for_columns(
            start_col_offset=EventWorksheetColumnOffsets.PLAYER,
            end_col_offset=EventWorksheetColumnOffsets.EVENT_RANK,
        )

        sort_spec = google_sheet.SortSpec(
            column=self._column_letter_for_offset(EventWorksheetColumnOffsets.EVENT_RANK),
            order=google_sheet.SortOrder.ASCENDING,
        )

        self._worksheet.sort_range(specs=[sort_spec], range_name=sort_range)
