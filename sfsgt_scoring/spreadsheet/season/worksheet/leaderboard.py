from typing import NamedTuple

from gspread import utils as gspread_utils

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
    wins: int
    top_5s: int
    top_10s: int
    # dict keys are event names - should be verified by SeasonSheet class before writing
    event_points: dict[str, float]


Events = dict[int, str]  # Map of event numbers to event names
PlayerEventPoints = dict[str, float]  # Map of event names to event points for a player

FIRST_PLAYER_ROW = 3
PLAYER_SECTION_START_COLUMN = "B"
PLAYER_SECTION_END_COLUMN = "I"
EVENTS_SECTION_START_COLUMN = "K"


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

    def _last_player_row(self) -> int:
        num_players = len(self._players)
        return FIRST_PLAYER_ROW + num_players - 1

    def write(self, write_data: LeaderboardWriteData) -> None:
        self.verify_write_data(write_data)

        sorted_player_data = write_data.players_sorted_by_rank()

        players_write_range = self.players_write_range(sorted_player_data)
        events_write_range = self.events_write_range(sorted_player_data)
        write_ranges = [players_write_range, events_write_range]

        self._worksheet.write_multiple_ranges(write_ranges)

    def verify_write_data(self, write_data: LeaderboardWriteData) -> None:
        write_data_players: list[str] = write_data.player_names()
        write_data_players_deduplicated = list(set(write_data_players))
        if not len(write_data_players) == len(write_data_players_deduplicated):
            raise LeaderboardWorksheetWriteError(
                "Duplicate player names found in write data."
            )

        if not sorted(write_data_players_deduplicated) == sorted(self._players):
            raise LeaderboardWorksheetWriteError(
                "Player names in write data do not match expected players."
            )

        for player_data in write_data.players:
            player_events = list(player_data.event_points.keys())
            if player_events != self._sorted_event_names:
                raise LeaderboardWorksheetWriteError(
                    f"Player '{player_data.player_name}' does not have expected event scores.\n"
                    f"Expected: {self._sorted_event_names}\nFound: {player_events}"
                )

    def players_write_range(self, sorted_player_data: list[PlayerLeaderboardWriteData]) -> worksheet.RangeValues:
        range_start = PLAYER_SECTION_START_COLUMN + str(FIRST_PLAYER_ROW)
        range_end = PLAYER_SECTION_END_COLUMN + str(self._last_player_row())
        range_name = f"{range_start}:{range_end}"

        values: list[list[worksheet.CellValueType]] = []
        for data in sorted_player_data:
            value: list[worksheet.CellValueType] = [
                data.season_rank,
                data.player_name,
                data.season_points,
                data.events_played,
                data.birdies,
                data.wins,
                data.top_5s,
                data.top_10s,
            ]
            values.append(value)

        return worksheet.RangeValues(
            range=range_name,
            values=values,
        )

    def events_write_range(self, sorted_player_data: list[PlayerLeaderboardWriteData]) -> worksheet.RangeValues:
        range_start = EVENTS_SECTION_START_COLUMN + str(FIRST_PLAYER_ROW)

        start_col_idx = gspread_utils.column_letter_to_index(EVENTS_SECTION_START_COLUMN)
        end_col_idx = start_col_idx + len(self._sorted_event_names) - 1

        range_end = gspread_utils.rowcol_to_a1(row=self._last_player_row(), col=end_col_idx)

        range_name = f"{range_start}:{range_end}"

        values: list[list[worksheet.CellValueType]] = []
        for data in sorted_player_data:
            value: list[worksheet.CellValueType] = [
                data.event_points[event_name] for event_name in self._sorted_event_names
            ]
            values.append(value)

        return worksheet.RangeValues(
            range=range_name,
            values=values
        )
