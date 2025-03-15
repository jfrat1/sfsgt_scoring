from typing import NamedTuple

import google_sheet

from season_view.api import read_data, view, write_data
from season_view.google_sheet_view import worksheets


class GoogleSheetSeasonViewEventConfig(NamedTuple):
    event_number: int
    event_name: str
    worksheet_name: str
    scorecard_start_cell: str


class GoogleSheetSeasonViewConfig(NamedTuple):
    leaderboard_worksheet_name: str
    players_worksheet_name: str
    event_worksheet_configs: list[GoogleSheetSeasonViewEventConfig]

    def worksheet_names(self) -> list[str]:
        event_worksheet_names = {event.worksheet_name for event in self.event_worksheet_configs}
        return list(
            {
                self.players_worksheet_name,
                self.leaderboard_worksheet_name,
            }.union(event_worksheet_names)
        )

    @property
    def event_names(self) -> list[str]:
        return [event.event_name for event in self.event_worksheet_configs]

    @property
    def ordered_event_names(self) -> list[str]:
        ordered_event_configs = sorted(self.event_worksheet_configs, key=lambda event: event.event_number)
        return [event.event_name for event in ordered_event_configs]

    def event_config(self, event_name: str) -> GoogleSheetSeasonViewEventConfig:
        for event_cfg in self.event_worksheet_configs:
            if event_cfg.event_name == event_name:
                return event_cfg

        raise ValueError(f"No event named {event_name} can be found.")


class GoogleSheetSeasonViewError(Exception):
    pass


class GoogleSheetSeasonView(view.SeasonView):
    def __init__(
        self,
        config: GoogleSheetSeasonViewConfig,
        sheet_controller: google_sheet.GoogleSheetController,
    ) -> None:
        self._config = config
        self._sheet_controller = sheet_controller
        self._verify_available_worksheets()

        # The event worksheet state needs to be held between read and write events.
        # These will be instantiated after the players sheet is read.
        self._event_worksheets: dict[str, worksheets.EventWorksheet] = {}

    def read_season(self) -> read_data.SeasonViewReadData:
        players_data = self._read_players_worksheet()

        self._event_worksheets = self._generate_event_worksheets(players_data.player_names)
        events_data = self._read_event_worksheets()

        return read_data.SeasonViewReadData(
            players=players_data,
            events=events_data,
        )

    def write_season(self, data: write_data.SeasonViewWriteData) -> None:
        if len(self._event_worksheets) == 0:
            raise GoogleSheetSeasonViewError(
                f"An unexpected error has occurred. This error suggests that a {self.__class__.__name__} "
                "instance was not read before it was written to. Check your implementation to ensure that "
                "a read event occurs before a write event."
            )

        for event in self._config.event_names:
            worksheet = self._event_worksheets[event]
            event_data = data.get_event(event_name=event)

            worksheet.write(data=event_data)

        leaderboard_worksheet_controller = self._sheet_controller.worksheet(self._config.leaderboard_worksheet_name)
        worksheets.LeaderboardWorksheet(
            data=data.leaderboard,
            worksheet_controller=leaderboard_worksheet_controller,
            ordered_event_names=self._config.ordered_event_names,
        ).write()

    def _verify_available_worksheets(self) -> None:
        required_worksheets = set(self._config.worksheet_names())
        available_worksheets = set(self._sheet_controller.worksheet_titles())

        missing_worksheets = required_worksheets.difference(available_worksheets)

        if len(missing_worksheets) > 0:
            raise GoogleSheetSeasonViewError(
                f"Some required worksheets are not available. Missing worksheets: {missing_worksheets}"
            )

    def _read_players_worksheet(self) -> read_data.SeasonViewReadPlayers:
        players_worksheet_controller = self._sheet_controller.worksheet(self._config.players_worksheet_name)

        return worksheets.PlayersWorksheet(
            worksheet_controller=players_worksheet_controller,
            events=self._config.event_names,
        ).read()

    def _generate_event_worksheets(self, players: list[str]) -> dict[str, worksheets.EventWorksheet]:
        event_worksheets: dict[str, worksheets.EventWorksheet] = {}
        for event in self._config.event_names:
            event_config = self._config.event_config(event_name=event)
            event_worksheet_controller = self._sheet_controller.worksheet(event_config.worksheet_name)
            event_worksheets[event] = worksheets.EventWorksheet(
                event_name=event,
                worksheet_controller=event_worksheet_controller,
                scorecard_start_cell=event_config.scorecard_start_cell,
                players=players,
            )

        return event_worksheets

    def _read_event_worksheets(self) -> read_data.SeasonViewReadEvents:
        events_data: dict[str, read_data.SeasonViewReadEvent] = {}
        for event in self._config.event_names:
            events_data[event] = self._event_worksheets[event].read()

        return read_data.SeasonViewReadEvents(events_data)
