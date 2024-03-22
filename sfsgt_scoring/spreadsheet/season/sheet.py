from typing import NamedTuple

from sfsgt_scoring.spreadsheet import google
from sfsgt_scoring.spreadsheet.season import read_data, write_data, worksheet


class SeasonSheetConfig(NamedTuple):
    sheet_id: str
    leaderboard_sheet_name: str
    players_sheet_name: str
    events: list[str]


class SeasonSheetVerificationError(Exception):
    """Exception to be raised if the structure or data of the season sheet is not valid."""


class SeasonSheet:
    def __init__(self, config: SeasonSheetConfig) -> None:
        self.google_sheet = google.GoogleSheet(sheet_id=config.sheet_id)
        self.config = config

        self._verify_available_worksheets()

    def _verify_available_worksheets(self) -> None:
        event_worksheets = {f"{event} Scorecard" for event in self.config.events}
        required_worksheets = {
            self.config.leaderboard_sheet_name,
            self.config.players_sheet_name,
        }.union(event_worksheets)
        available_worksheets = self.google_sheet.worksheet_titles()

        if not required_worksheets.issubset(available_worksheets):
            missing_worksheets = required_worksheets.difference(available_worksheets)
            raise SeasonSheetVerificationError(
                f"Some required worksheets are missing: {missing_worksheets}"
            )

    def read(self) -> read_data.SeasonSheetReadData:
        pass

    def write(self, data: write_data.SeasonSheetWriteData) -> None:
        pass


class SeasonWorksheets(NamedTuple):
    players: worksheet.PlayersWorksheet
    leaderboard: worksheet.LeaderboardWorksheet
    events: dict[str, worksheet.EventWorksheet]

