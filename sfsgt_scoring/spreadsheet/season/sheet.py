from typing import NamedTuple

from sfsgt_scoring.spreadsheet import google
from sfsgt_scoring.spreadsheet.season import worksheet


class SeasonSheetReadData(NamedTuple):
    players: worksheet.PlayersReadData
    events: "SeasonEventsReadData"

    def player_names(self) -> list[str]:
        return self.players.player_names()

    def event_names(self) -> list[str]:
        return list(self.events.keys())


SeasonEventsReadData = dict[str, worksheet.EventReadData]


class SeasonSheetWriteData(NamedTuple):
    leaderboard: worksheet.LeaderboardWriteData
    events: "SeasonEventsWriteData"


SeasonEventsWriteData = dict[str, worksheet.EventWriteData]


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

    def event_names(self) -> list[str]:
        return list(self.events.keys())


class SeasonSheetEventConfig(NamedTuple):
    event_num: int
    sheet_name: str
    scorecard_start_cell: str


class SeasonSheetNotConfiguredError(Exception):
    """Exception to be raised when actions are taken on a season sheet before it has been configured."""


class SeasonSheetVerificationError(Exception):
    """Exception to be raised if the structure or data of the season sheet is not valid."""


class SeasonSheetWriteError(Exception):
    """Exception to be raised when an error is encountered while writing."""


class SeasonSheet:
    def __init__(self, config: SeasonSheetConfig | None = None) -> None:
        self.is_configured = False
        self.config: SeasonSheetConfig | None = None
        self.google_sheet: google.GoogleSheet | None = None
        self.worksheets: SeasonWorksheets | None = None

        if config is not None:
            self.configure(config)

    def configure(self, config: SeasonSheetConfig) -> None:
        google_sheet = google.GoogleSheet(sheet_id=config.sheet_id)

        self._verify_available_worksheets(config=config, google_sheet=google_sheet)
        self.worksheets = self._create_worksheets(config=config, google_sheet=google_sheet)

        self.config = config
        self.google_sheet = google_sheet
        self.is_configured = True

    def _verify_available_worksheets(self, config: SeasonSheetConfig, google_sheet: google.GoogleSheet) -> None:
        event_worksheets = {f"{event.sheet_name}" for event in config.events.values()}
        required_worksheets = {
            config.leaderboard_sheet_name,
            config.players_sheet_name,
        }.union(event_worksheets)
        available_worksheets = google_sheet.worksheet_titles()

        if not required_worksheets.issubset(available_worksheets):
            missing_worksheets = required_worksheets.difference(available_worksheets)
            raise SeasonSheetVerificationError(
                f"Some required worksheets are missing: {missing_worksheets}"
            )

    def _create_worksheets(self, config: SeasonSheetConfig, google_sheet: google.GoogleSheet) -> "SeasonWorksheets":
        players_worksheet = self._create_players_worksheet(config=config, google_sheet=google_sheet)
        player_names = players_worksheet.player_names()
        return SeasonWorksheets(
            players=players_worksheet,
            leaderboard=self._create_leaderboard_worksheet(
                config=config, google_sheet=google_sheet, player_names=player_names
            ),
            events=self._create_event_worksheets(
                config=config, google_sheet=google_sheet, player_names=player_names
            ),
        )

    def _create_players_worksheet(
        self,
        config: SeasonSheetConfig,
        google_sheet: google.GoogleSheet,
    ) -> worksheet.PlayersWorksheet:
        google_worksheet = google_sheet.worksheet(worksheet_name=config.players_sheet_name)
        return worksheet.PlayersWorksheet(
            worksheet=google_worksheet,
            events=config.event_names(),
        )

    def _create_leaderboard_worksheet(
        self,
        config: SeasonSheetConfig,
        google_sheet: google.GoogleSheet,
        player_names: list[str],
    ) -> worksheet.LeaderboardWorksheet:
        google_worksheet = google_sheet.worksheet(worksheet_name=config.leaderboard_sheet_name)
        return worksheet.LeaderboardWorksheet(
            worksheet=google_worksheet,
            players=player_names,
            events={
                event_data.event_num: event_name
                for event_name, event_data in config.events.items()
            },
        )

    def _create_event_worksheets(
        self,
        config: SeasonSheetConfig,
        google_sheet: google.GoogleSheet,
        player_names: list[str],
    ) -> "EventWorksheets":
        event_worksheets = {
            event_name: self._create_event_worksheet(
                event_config=event_config, google_sheet=google_sheet, player_names=player_names
            ) for event_name, event_config in config.events.items()
        }

        return EventWorksheets(event_worksheets)

    def _create_event_worksheet(
        self,
        event_config: SeasonSheetEventConfig,
        google_sheet: google.GoogleSheet,
        player_names: list[str],
    ) -> worksheet.EventWorksheet:
        google_worksheet = google_sheet.worksheet(worksheet_name=event_config.sheet_name)
        return worksheet.EventWorksheet(
            worksheet=google_worksheet,
            players=player_names,
            scorecard_start_cell=event_config.scorecard_start_cell,
        )

    def _verify_is_configured(self):
        if not self.is_configured:
            raise SeasonSheetNotConfiguredError(
                "The season sheet must be configured before executing this method. "
                "Please run 'configure' on the object first."
            )

    def read(self) -> SeasonSheetReadData:
        self._verify_is_configured()

        assert self.worksheets is not None  # This is here to satisfy mypy. It should not be reachable.

        return SeasonSheetReadData(
            players=self.worksheets.players.read(),
            events=self.worksheets.events.read(),
        )

    def write(self, data: SeasonSheetWriteData) -> None:
        if self.worksheets is None:
            raise SeasonSheetWriteError(
                "An unexpected error was encountered while writing to the spreadsheet. Ensure that "
                "this class instance has been configured before writing."
            )

        self.worksheets.leaderboard.write(write_data=data.leaderboard)

        for event_name, event_worksheet in self.worksheets.events.items():
            event_write_data = data.events[event_name]
            event_worksheet.write(event_write_data)
