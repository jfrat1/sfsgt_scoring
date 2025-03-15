import enum

import google_sheet
from google_sheet import utils as sheet_utils

from season_view.api.write_data import SeasonViewWriteLeaderboard, SeasonViewWriteLeaderboardPlayer


class LeaderboardColumns(enum.Enum):
    SEASON_RANK = "B"
    PLAYER_NAME = "C"
    SEASON_POINTS = "D"
    NUM_BIRDIES = "E"
    EVENTS_PLAYED = "G"
    EVENT_WINS = "H"
    EVENT_TOP_FIVES = "I"
    EVENT_TOP_TENS = "J"
    NET_STROKES_WINS = "L"
    NET_STROKES_TOP_FIVES = "M"
    NET_STROKES_TOP_TENS = "N"
    FIRST_EVENT = "P"

    def __str__(self) -> str:
        return self.value

    def __add__(self, other: str) -> str:
        return str(self) + other


FIRST_PLAYER_ROW = 4


class LeadberboardWorksheetError(Exception):
    pass


class LeaderboardWorksheet:
    def __init__(
        self,
        data: SeasonViewWriteLeaderboard,
        worksheet_controller: google_sheet.GoogleWorksheet,
        ordered_event_names: list[str],
    ) -> None:
        self._data = data
        self._worksheet_controller = worksheet_controller
        self._ordered_event_names = ordered_event_names

    def write(self) -> None:
        sorted_player_data = self._data.players_rank_sorted()

        write_ranges = [
            self._standings_write_range(sorted_player_data),
            self._event_finishes_write_range(sorted_player_data),
            self._net_strokes_finishes_write_range(sorted_player_data),
            self._event_points_write_range(sorted_player_data),
        ]
        self._worksheet_controller.write_multiple_ranges(write_ranges)

    def _standings_write_range(
        self,
        sorted_player_data: list[SeasonViewWriteLeaderboardPlayer],
    ) -> google_sheet.RangeValues:
        range_start = LeaderboardColumns.SEASON_RANK + str(self._first_player_row())
        range_end = LeaderboardColumns.NUM_BIRDIES + str(self._last_player_row())
        range_name = f"{range_start}:{range_end}"

        values: list[list[google_sheet.CellValueType]] = []
        for player_data in sorted_player_data:
            value: list[google_sheet.CellValueType] = [
                player_data.season_rank,
                player_data.name,
                player_data.season_points,
                player_data.birdies,
            ]
            values.append(value)

        return google_sheet.RangeValues(
            range=range_name,
            values=values,
        )

    def _event_finishes_write_range(
        self, sorted_player_data: list[SeasonViewWriteLeaderboardPlayer]
    ) -> google_sheet.RangeValues:
        range_start = LeaderboardColumns.EVENTS_PLAYED + str(self._first_player_row())
        range_end = LeaderboardColumns.EVENT_TOP_TENS + str(self._last_player_row())
        range_name = f"{range_start}:{range_end}"

        values: list[list[google_sheet.CellValueType]] = []
        for data in sorted_player_data:
            value: list[google_sheet.CellValueType] = [
                data.events_played,
                data.event_wins,
                data.event_top_fives,
                data.event_top_tens,
            ]
            values.append(value)

        return google_sheet.RangeValues(
            range=range_name,
            values=values,
        )

    def _net_strokes_finishes_write_range(
        self, sorted_player_data: list[SeasonViewWriteLeaderboardPlayer]
    ) -> google_sheet.RangeValues:
        range_start = LeaderboardColumns.NET_STROKES_WINS + str(self._first_player_row())
        range_end = LeaderboardColumns.NET_STROKES_TOP_TENS + str(self._last_player_row())
        range_name = f"{range_start}:{range_end}"

        values: list[list[google_sheet.CellValueType]] = []
        for data in sorted_player_data:
            value: list[google_sheet.CellValueType] = [
                data.net_strokes_wins,
                data.net_strokes_top_fives,
                data.net_strokes_top_tens,
            ]
            values.append(value)

        return google_sheet.RangeValues(
            range=range_name,
            values=values,
        )

    def _event_points_write_range(
        self, sorted_player_data: list[SeasonViewWriteLeaderboardPlayer]
    ) -> google_sheet.RangeValues:
        start_col = str(LeaderboardColumns.FIRST_EVENT)
        start_col_idx = sheet_utils.column_letter_to_idx(start_col)
        end_col_idx = start_col_idx + len(self._ordered_event_names) - 1

        range_start = LeaderboardColumns.FIRST_EVENT + str(self._first_player_row())
        range_end = sheet_utils.column_idx_to_letter(end_col_idx) + str(self._last_player_row())
        range_name = f"{range_start}:{range_end}"

        values: list[list[google_sheet.CellValueType]] = []
        for data in sorted_player_data:
            value: list[google_sheet.CellValueType] = [
                data.event_points[event_name] for event_name in self._ordered_event_names
            ]
            values.append(value)

        return google_sheet.RangeValues(range=range_name, values=values)

    def _first_player_row(self) -> int:
        return FIRST_PLAYER_ROW

    def _last_player_row(self) -> int:
        num_players = self._data.num_players
        return self._first_player_row() + num_players - 1
