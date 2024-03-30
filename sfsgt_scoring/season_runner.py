from sfsgt_scoring import season_config, season, spreadsheet


class SeasonRunner:
    """Season runner class responsible for processing a season and updating its spreadsheet.

    Design thoughts:
    - should construct/hold a sheet controller object - to read and write data to the sheet
      - may need to consider a few layers of abstraction down this leg to separate the
        business logic (read player + scorecard data, write event + season results) from
        low-level logic (read/write specific cells from a specific sheet)

    - should construct/hold a season object - to calculate results data for the season


    """

    def __init__(self, season_cfg: season_config.SeasonConfig) -> None:
        self.season_cfg = season_cfg
        self.season_sheet = self._season_sheet()

    def _season_sheet(self) -> spreadsheet.SeasonSheet:
        # Consider not reaching so far into the season config
        event_configs = self._event_configs()
        sheet_config = self._season_sheet_config(event_configs)
        return spreadsheet.SeasonSheet(config=sheet_config)

    def _season_sheet_config(
        self, event_configs: dict[str, spreadsheet.SeasonSheetEventConfig]
    ) -> spreadsheet.SeasonSheetConfig:
        return spreadsheet.SeasonSheetConfig(
            sheet_id=self.season_cfg.sheet_id,
            leaderboard_sheet_name=self.season_cfg.leaderboard_sheet_name,
            players_sheet_name=self.season_cfg.players_sheet_name,
            events=event_configs,
        )

    def _event_configs(self) -> dict[str, spreadsheet.SeasonSheetEventConfig]:
        return {
            event.event_name: spreadsheet.SeasonSheetEventConfig(
                sheet_name=event.sheet_name,
                scorecard_start_cell=event.scorecard_sheet_start_cell,
            ) for event in self.season_cfg.event_configs()
        }

    def run(self) -> None:
        sheet_read_data = self._read_spreadsheet_data()
        season = self._create_season(spreadsheet_data=sheet_read_data)
        season_results = season.results()
        self._write_spreadsheet_data(season_results=season_results)
        pass

    def _read_spreadsheet_data(self) -> spreadsheet.SeasonSheetReadData:
        return self.season_sheet.read()

    def _create_season(self, spreadsheet_data: spreadsheet.SeasonSheetReadData) -> season.Season:
        pass

    def _write_spreadsheet_data(self, season_results: season.SeasonResults) -> None:
        pass
