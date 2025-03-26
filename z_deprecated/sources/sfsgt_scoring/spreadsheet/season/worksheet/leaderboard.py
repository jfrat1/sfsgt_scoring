import enum
from typing import NamedTuple

from sfsgt_scoring.spreadsheet import sheet_utils
from sfsgt_scoring.spreadsheet.google import worksheet


class LeaderboardWriteData(NamedTuple):
    players: list["PlayerLeaderboardWriteData"]

    def players_sorted_by_rank(self) -> list["PlayerLeaderboardWriteData"]:
        return sorted(self.players, key=lambda player: player.season_rank)

    def player_names(self) -> list[str]:
        return [player.player_name for player in self.players]


class PlayerLeaderboardWriteData(NamedTuple):
    player_name: str
    season_points: float
    season_rank: int
    events_played: int
    birdies: int
    eagles: int
    net_strokes_wins: int
    net_strokes_top_fives: int
    net_strokes_top_tens: int
    event_wins: int
    event_top_fives: int
    event_top_tens: int
    # dict keys are event names - should be verified by SeasonSheet class before writing
    event_points: dict[str, float]


Events = dict[int, str]  # Map of event numbers to event names
PlayerEventPoints = dict[str, float]  # Map of event names to event points for a player


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


class LeaderboardWorksheetWriteError(Exception):
    """Exception to be raised when an error is encountered while writing a leaderboard workshet."""


class LeaderboardWorksheet:
    def __init__(
        self,
        worksheet: worksheet.GoogleWorksheet,
        players: list[str],
        events: Events,
    ) -> None:
        self._worksheet = worksheet
        self._players = players
        self._sorted_event_names = [events[key] for key in sorted(events.keys())]

    def _first_player_row(self) -> int:
        return FIRST_PLAYER_ROW

    def _last_player_row(self) -> int:
        num_players = len(self._players)
        return self._first_player_row() + num_players - 1

    def write(self, write_data: LeaderboardWriteData) -> None:
        self.verify_write_data(write_data)

        sorted_player_data = write_data.players_sorted_by_rank()

        write_ranges = [
            self._standings_write_range(sorted_player_data),
            self._event_finishes_write_range(sorted_player_data),
            self._net_strokes_finishes_write_range(sorted_player_data),
            self._event_points_write_range(sorted_player_data),
        ]

        self._worksheet.write_multiple_ranges(write_ranges)

    def verify_write_data(self, write_data: LeaderboardWriteData) -> None:
        write_data_players: list[str] = write_data.player_names()
        write_data_players_deduplicated = list(set(write_data_players))
        if not len(write_data_players) == len(write_data_players_deduplicated):
            raise LeaderboardWorksheetWriteError("Duplicate player names found in write data.")

        if not sorted(write_data_players_deduplicated) == sorted(self._players):
            raise LeaderboardWorksheetWriteError("Player names in write data do not match expected players.")

        for player_data in write_data.players:
            player_events = list(player_data.event_points.keys())
            if player_events != self._sorted_event_names:
                raise LeaderboardWorksheetWriteError(
                    f"Player '{player_data.player_name}' does not have expected event scores.\n"
                    f"Expected: {self._sorted_event_names}\nFound: {player_events}"
                )

    def _standings_write_range(self, sorted_player_data: list[PlayerLeaderboardWriteData]) -> worksheet.RangeValues:
        range_start = LeaderboardColumns.SEASON_RANK + str(self._first_player_row())
        range_end = LeaderboardColumns.NUM_BIRDIES + str(self._last_player_row())
        range_name = f"{range_start}:{range_end}"

        values: list[list[worksheet.CellValueType]] = []
        for data in sorted_player_data:
            value: list[worksheet.CellValueType] = [
                data.season_rank,
                data.player_name,
                data.season_points,
                data.birdies,
            ]
            values.append(value)

        return worksheet.RangeValues(
            range=range_name,
            values=values,
        )

    def _event_finishes_write_range(
        self, sorted_player_data: list[PlayerLeaderboardWriteData]
    ) -> worksheet.RangeValues:
        range_start = LeaderboardColumns.EVENTS_PLAYED + str(self._first_player_row())
        range_end = LeaderboardColumns.EVENT_TOP_TENS + str(self._last_player_row())
        range_name = f"{range_start}:{range_end}"

        values: list[list[worksheet.CellValueType]] = []
        for data in sorted_player_data:
            value: list[worksheet.CellValueType] = [
                data.events_played,
                data.event_wins,
                data.event_top_fives,
                data.event_top_tens,
            ]
            values.append(value)

        return worksheet.RangeValues(
            range=range_name,
            values=values,
        )

    def _net_strokes_finishes_write_range(
        self, sorted_player_data: list[PlayerLeaderboardWriteData]
    ) -> worksheet.RangeValues:
        range_start = LeaderboardColumns.NET_STROKES_WINS + str(self._first_player_row())
        range_end = LeaderboardColumns.NET_STROKES_TOP_TENS + str(self._last_player_row())
        range_name = f"{range_start}:{range_end}"

        values: list[list[worksheet.CellValueType]] = []
        for data in sorted_player_data:
            value: list[worksheet.CellValueType] = [
                data.net_strokes_wins,
                data.net_strokes_top_fives,
                data.net_strokes_top_tens,
            ]
            values.append(value)

        return worksheet.RangeValues(
            range=range_name,
            values=values,
        )

    def _event_points_write_range(self, sorted_player_data: list[PlayerLeaderboardWriteData]) -> worksheet.RangeValues:
        start_col = str(LeaderboardColumns.FIRST_EVENT)
        start_col_idx = sheet_utils.column_letter_to_idx(start_col)
        end_col_idx = start_col_idx + len(self._sorted_event_names) - 1

        range_start = LeaderboardColumns.FIRST_EVENT + str(self._first_player_row())
        range_end = sheet_utils.column_idx_to_letter(end_col_idx) + str(self._last_player_row())
        range_name = f"{range_start}:{range_end}"

        values: list[list[worksheet.CellValueType]] = []
        for data in sorted_player_data:
            value: list[worksheet.CellValueType] = [
                data.event_points[event_name] for event_name in self._sorted_event_names
            ]
            values.append(value)

        return worksheet.RangeValues(range=range_name, values=values)
