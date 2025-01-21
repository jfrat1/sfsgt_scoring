import enum
from typing import Any

import pandas as pd

import google_sheet
from google_sheet import utils as sheet_utils
from season_common import scorecard
from season_view.api import read_data, write_data

STANDARD_HOLE_CELL_FORMAT = google_sheet.CellFormat(
    backgroundColor=google_sheet.ColorRgb(
        red=252,
        green=245,
        blue=243,
    ),
)

BIRDIE_HOLE_CELL_FORMAT = google_sheet.CellFormat(
    backgroundColor=google_sheet.ColorRgb(
        red=217,
        green=234,
        blue=211,
    ),
)

EAGLE_HOLE_CELL_FORMAT = google_sheet.CellFormat(
    backgroundColor=google_sheet.ColorRgb(
        red=255,
        green=187,
        blue=137,
    ),
)


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


EVENT_WORKSHEET_COLUMN_NAMES = [e.name for e in EventWorksheetColumnOffsets]

READ_DATA_FIRST_COLUMN = "PLAYER"
READ_DATA_LAST_COLUMN = "HOLE_18"
READ_DATA_FIRST_COL_INDEX = EVENT_WORKSHEET_COLUMN_NAMES.index(READ_DATA_FIRST_COLUMN)
READ_DATA_LAST_COL_INDEX = EVENT_WORKSHEET_COLUMN_NAMES.index(READ_DATA_LAST_COLUMN)


class EventWorksheetError(Exception):
    pass


class EventWorksheet:
    def __init__(
        self,
        event_name: str,
        worksheet_controller: google_sheet.GoogleWorksheet,
        scorecard_start_cell: str,
        players: list[str],
    ) -> None:
        self._event_name = event_name
        self._worksheet_controller = worksheet_controller
        self._scorecard_start_cell = scorecard_start_cell
        self._players = players

        self._verify_start_cell()

        # The player order must be stored between read and write events to ensure
        # that results are placed in the correct locations.
        self._players_ordered_at_read_time: list[str] = []

    def _verify_start_cell(self) -> None:
        if not sheet_utils.is_cell_a1_notation(self._scorecard_start_cell):
            raise EventWorksheetError(f"Scorecard start cell must be in A1 notation: {self._scorecard_start_cell}")

    def read(self) -> read_data.SeasonViewReadEvent:
        reader = EventWorksheetReader(
            event_name=self._event_name,
            worksheet_controller=self._worksheet_controller,
            scorecard_start_cell=self._scorecard_start_cell,
            players=self._players,
        )
        data = reader.read()
        self._players_ordered_at_read_time = reader.players_ordered_at_read_time

        return data

    def write(self, data: write_data.SeasonViewWriteEvent) -> None:
        if len(self._players_ordered_at_read_time) == 0:
            raise EventWorksheetError(
                f"An unexpected error has occurred. This error suggests that a {self.__class__.__name__} "
                "instance was not read before it was written to. Check your implementation to ensure that "
                "a read event occurs before a write event."
            )

        EventWorksheetWriter(
            data=data,
            worksheet_controller=self._worksheet_controller,
            scorecard_start_cell=self._scorecard_start_cell,
            players_ordered_at_read_time=self._players_ordered_at_read_time,
        ).write()


class EventWorksheetReader:
    def __init__(
        self,
        event_name: str,
        worksheet_controller: google_sheet.GoogleWorksheet,
        scorecard_start_cell: str,
        players: list[str],
    ) -> None:
        self._event_name = event_name
        self._worksheet_controller = worksheet_controller
        self._scorecard_start_cell = scorecard_start_cell
        self._players = players

        self._players_ordered_at_read_time: list[str] = []

    def read(self) -> read_data.SeasonViewReadEvent:
        raw_data = self._raw_worksheet_data()
        data = self._process_raw_worksheet_data(raw_data)
        self._check_worksheet_data(data)

        self._set_players_ordered_at_read_time(data.index)

        data_mod = sheet_utils.replace_empty_strings_with_none(data)

        # TODO: This cycolmatic complexity stinks.
        scorecards: dict[str, scorecard.Scorecard] = {}
        for player in self._players:
            if player in data_mod.index:
                player_data = data_mod.loc[player]
                if player_data.empty or any(player_data.isna()):
                    scorecards[player] = scorecard.IncompleteScorecard()
                else:
                    hole_scores = {
                        int(hole_name.replace("HOLE_", "")): int(hole_score)
                        for hole_name, hole_score in dict(player_data).items()
                    }
                    scorecards[player] = scorecard.scorecard_factory(hole_scores=hole_scores)
            else:
                scorecards[player] = scorecard.IncompleteScorecard()

        return read_data.SeasonViewReadEvent(
            event_name=self._event_name,
            player_scorecards=scorecards,
        )

    def _set_players_ordered_at_read_time(self, read_index: pd.Index) -> None:
        # Drop empty player names. These indicate missing players in the worksheet.
        read_index_no_empties = read_index.delete(read_index == "")
        read_players_ordered = list(read_index_no_empties)

        missing_players = set(self._players).difference(set(read_players_ordered))

        # Players that exist in the sheet retain their original order.
        # Missing players are sorted by name.
        self._players_ordered_at_read_time = read_players_ordered + sorted(missing_players)

    @property
    def players_ordered_at_read_time(self) -> list[str]:
        if len(self._players_ordered_at_read_time) == 0:
            raise EventWorksheetError("The `read` method must be called before this property is accessed.")
        return self._players_ordered_at_read_time

    def _raw_worksheet_data(self) -> pd.DataFrame:
        return self._worksheet_controller.range_to_df(range=self._read_range())

    def _read_range(self) -> str:
        return f"{self._scorecard_start_cell}:{self._read_range_end_cell()}"

    def _read_range_end_cell(self) -> str:
        (start_row, start_col) = sheet_utils.a1_to_rowcol(self._scorecard_start_cell)

        end_row = start_row + self._read_range_row_offset()
        end_col = start_col + self._read_range_col_offset()
        return sheet_utils.rowcol_to_a1(row=end_row, col=end_col)

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
        column_labels = EVENT_WORKSHEET_COLUMN_NAMES[READ_DATA_FIRST_COL_INDEX : READ_DATA_LAST_COL_INDEX + 1]
        worksheet_data.columns = pd.Index(column_labels)
        worksheet_data.drop(columns=["FRONT_NINE_STROKES", "PLAYER_INITIAL"], inplace=True)
        worksheet_data.set_index(keys="PLAYER", inplace=True)

        return sheet_utils.numericise_all_values(worksheet_data)

    def _check_worksheet_data(self, worksheet_data: pd.DataFrame) -> None:
        self._check_column_headers(worksheet_data)
        self._check_data_values(worksheet_data)

    def _check_column_headers(self, worksheet_data: pd.DataFrame) -> None:
        expected_columns = [f"HOLE_{str(hole_num)}" for hole_num in range(1, 19)]
        if not list(worksheet_data.columns) == expected_columns:
            raise EventWorksheetError(
                f"Worksheet data column labels do not match expectations."
                f"\nExpected: {expected_columns}, \nFound:{worksheet_data.columns}"
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
            raise EventWorksheetError(
                "Cell values in the event worksheet must be numeric values or empty."
                f"The value at row: {row_name}, col: {col_name} is invalid. Found: {value}"
            )


class EventWorksheetWriter:
    def __init__(
        self,
        data: write_data.SeasonViewWriteEvent,
        worksheet_controller: google_sheet.GoogleWorksheet,
        scorecard_start_cell: str,
        players_ordered_at_read_time: list[str],
    ) -> None:
        self._data = data
        self._worksheet_controller = worksheet_controller
        self._scorecard_start_cell = scorecard_start_cell
        self._players_ordered_at_read_time = players_ordered_at_read_time

    def write(self) -> None:
        write_ranges = [
            self._player_names_write_range(),
            self._front_nine_write_range(data=self._data),
            self._back_nine_and_event_results_write_range(data=self._data),
        ]
        self._worksheet_controller.write_multiple_ranges(write_ranges)

    def _write_scorecard_data(self, write_data: write_data.SeasonViewWriteEvent):
        first_write_range = self._front_nine_write_range(write_data)
        second_write_range = self._back_nine_and_event_results_write_range(write_data)
        write_ranges = [first_write_range, second_write_range]

        self._worksheet_controller.write_multiple_ranges(write_ranges)

    def _player_names_write_range(self) -> google_sheet.RangeValues:
        range_name = self._range_for_columns(
            start_col_offset=EventWorksheetColumnOffsets.PLAYER,
            end_col_offset=EventWorksheetColumnOffsets.PLAYER,
        )
        values: list[list[google_sheet.CellValueType]] = [
            [player_name] for player_name in self._players_ordered_at_read_time
        ]

        return google_sheet.RangeValues(
            range=range_name,
            values=values,
        )

    def _front_nine_write_range(self, data: write_data.SeasonViewWriteEvent) -> google_sheet.RangeValues:
        range_name = self._range_for_columns(
            start_col_offset=EventWorksheetColumnOffsets.FRONT_NINE_STROKES,
            end_col_offset=EventWorksheetColumnOffsets.FRONT_NINE_STROKES,
        )

        values: list[list[google_sheet.CellValueType]] = []
        for player_name in self._players_ordered_at_read_time:
            player_data = data.get_player(player_name)
            is_complete = player_data.is_complete_event

            value: list[google_sheet.CellValueType] = [
                player_data.front_9_strokes if is_complete else "",
            ]
            values.append(value)

        return google_sheet.RangeValues(
            range=range_name,
            values=values,
        )

    def _back_nine_and_event_results_write_range(
        self,
        data: write_data.SeasonViewWriteEvent,
    ) -> google_sheet.RangeValues:
        range_name = self._range_for_columns(
            start_col_offset=EventWorksheetColumnOffsets.BACK_NINE_STROKES,
            end_col_offset=EventWorksheetColumnOffsets.EVENT_RANK,
        )

        values: list[list[google_sheet.CellValueType]] = []
        for player_name in self._players_ordered_at_read_time:
            player_data = data.get_player(player_name)
            is_complete = player_data.is_complete_event

            value: list[google_sheet.CellValueType] = [
                player_data.back_9_strokes if is_complete else "",
                player_data.gross_strokes if is_complete else "",
                player_data.course_handicap if is_complete else "",
                player_data.net_strokes if is_complete else "",
                player_data.gross_rank if is_complete else "N/A",
                player_data.net_rank if is_complete else "N/A",
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
        return sheet_utils.a1_to_rowcol(self._scorecard_start_cell)

    def _first_player_row(self) -> int:
        (row, _) = self._first_player_row_col()
        return row

    def _last_player_row(self) -> int:
        return self._first_player_row() + self._num_players() - 1

    def _column_letter_for_offset(self, col_offset: EventWorksheetColumnOffsets) -> str:
        (_, first_player_col) = self._first_player_row_col()
        col_idx = first_player_col + col_offset.value
        return sheet_utils.column_idx_to_letter(col_idx)

    def _num_players(self) -> int:
        return len(self._players_ordered_at_read_time)
