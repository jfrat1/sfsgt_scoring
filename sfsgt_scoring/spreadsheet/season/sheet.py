from typing import NamedTuple

from sfsgt_scoring.spreadsheet import google
from sfsgt_scoring.spreadsheet.season import worksheet


class SeasonSheetReadData(NamedTuple):
    players: worksheet.PlayersReadData
    events: "SeasonEventsReadData"


SeasonEventsReadData = dict[str, worksheet.EventReadData]


class SeasonSheetWriteData(NamedTuple):
    # same as above. write data for events and leaderboard
    pass


class SeasonWorksheets(NamedTuple):
    players: worksheet.PlayersWorksheet
    leaderboard: worksheet.LeaderboardWorksheet
    events: "EventWorksheets"


class EventWorksheets(dict[str, worksheet.EventWorksheet]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def read(self) -> SeasonEventsReadData:
        return {
            event_name: event_worksheet.read() for event_name, event_worksheet in self.items()
        }


class SeasonSheetConfig(NamedTuple):
    sheet_id: str
    leaderboard_sheet_name: str
    players_sheet_name: str
    events: dict[str, "SeasonSheetEventConfig"]

    def event_names(self) -> set[str]:
        return set(self.events.keys())


class SeasonSheetEventConfig(NamedTuple):
    sheet_name: str
    scorecard_start_cell: str


class SeasonSheetVerificationError(Exception):
    """Exception to be raised if the structure or data of the season sheet is not valid."""


class SeasonSheet:
    def __init__(self, config: SeasonSheetConfig) -> None:
        self.google_sheet = google.GoogleSheet(sheet_id=config.sheet_id)
        self.config = config

        self._verify_available_worksheets()
        self.worksheets = self._create_worksheets()

    def _verify_available_worksheets(self) -> None:
        event_worksheets = {f"{event.sheet_name}" for event in self.config.events.values()}
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

    def _create_worksheets(self) -> "SeasonWorksheets":
        players_worksheet = self._create_players_worksheet()
        player_names = players_worksheet.player_names()
        return SeasonWorksheets(
            players=players_worksheet,
            leaderboard=self._create_leaderboard_worksheet(player_names=player_names),
            events=self._create_event_worksheets(player_names=player_names),
        )

    def _create_players_worksheet(self) -> worksheet.PlayersWorksheet:
        google_worksheet = self.google_sheet.worksheet(worksheet_name=self.config.players_sheet_name)
        return worksheet.PlayersWorksheet(
            worksheet=google_worksheet,
            events=self.config.event_names(),
        )

    def _create_leaderboard_worksheet(self, player_names: set[str]) -> worksheet.LeaderboardWorksheet:
        google_worksheet = self.google_sheet.worksheet(worksheet_name=self.config.leaderboard_sheet_name)
        return worksheet.LeaderboardWorksheet(
            worksheet=google_worksheet,
            players=player_names,
        )

    def _create_event_worksheets(self, player_names: set[str]) -> "EventWorksheets":
        event_worksheets = {
            event_name: self._create_event_worksheet(event_config=event_config, player_names=player_names)
            for event_name, event_config in self.config.events.items()
        }

        return EventWorksheets(event_worksheets)

    def _create_event_worksheet(
        self,
        event_config: SeasonSheetEventConfig,
        player_names: set[str],
    ) -> worksheet.EventWorksheet:
        google_worksheet = self.google_sheet.worksheet(worksheet_name=event_config.sheet_name)
        return worksheet.EventWorksheet(
            worksheet=google_worksheet,
            players=player_names,
            scorecard_start_cell=event_config.scorecard_start_cell,
        )

    def read(self) -> SeasonSheetReadData:
        return SeasonSheetReadData(
            players=self.worksheets.players.read(),
            events=self.worksheets.events.read(),
        )

    def write(self, data: SeasonSheetWriteData) -> None:
        pass
