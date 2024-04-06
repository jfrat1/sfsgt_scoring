from sfsgt_scoring import course_database, season_config, season
from sfsgt_scoring.season import event as season_event
from sfsgt_scoring.spreadsheet import season as season_spreadsheet


class SeasonRunner:
    """Season runner class responsible for processing a season and updating its spreadsheet.

    Design thoughts:
    - should construct/hold a sheet controller object - to read and write data to the sheet
      - may need to consider a few layers of abstraction down this leg to separate the
        business logic (read player + scorecard data, write event + season results) from
        low-level logic (read/write specific cells from a specific sheet)

    - should construct/hold a season object - to calculate results data for the season


    """

    def __init__(
        self,
        config: season_config.SeasonConfig,
        sheet: season_spreadsheet.SeasonSheet,
        course_db: course_database.CourseDatabase,
    ) -> None:
        self.config = config
        self.sheet = sheet
        self.course_db = course_db

        self._configure_season_sheet()

    def _configure_season_sheet(self) -> None:
        event_configs = self._season_sheet_event_configs()
        sheet_config = self._season_sheet_config(event_configs)
        self.sheet.configure(sheet_config)

    def _season_sheet_event_configs(self) -> dict[str, season_spreadsheet.SeasonSheetEventConfig]:
        return {
            event.event_name: season_spreadsheet.SeasonSheetEventConfig(
                sheet_name=event.sheet_name,
                scorecard_start_cell=event.scorecard_sheet_start_cell,
            ) for event in self.config.event_configs()
        }

    def _season_sheet_config(
        self, event_configs: dict[str, season_spreadsheet.SeasonSheetEventConfig]
    ) -> season_spreadsheet.SeasonSheetConfig:
        return season_spreadsheet.SeasonSheetConfig(
            sheet_id=self.config.sheet_id,
            leaderboard_sheet_name=self.config.leaderboard_sheet_name,
            players_sheet_name=self.config.players_sheet_name,
            events=event_configs,
        )

    def run(self) -> None:
        sheet_read_data = self._read_spreadsheet_data()
        season = self._create_season(spreadsheet_data=sheet_read_data)
        season_results = season.results()
        self._write_spreadsheet_data(season_results=season_results)
        pass

    def _read_spreadsheet_data(self) -> season_spreadsheet.SeasonSheetReadData:
        return self.sheet.read()

    def _create_season(self, spreadsheet_data: season_spreadsheet.SeasonSheetReadData) -> season.Season:
        season_input = self._season_input(spreadsheet_data=spreadsheet_data)
        return season.Season(input=season_input)

    def _season_input(self, spreadsheet_data: season_spreadsheet.SeasonSheetReadData) -> season.SeasonInput:
        player_names = spreadsheet_data.player_names()
        event_names = spreadsheet_data.event_names()

        events = {
            event: self._event_input(
                event_name=event,
                player_names=player_names,
                spreadsheet_data=spreadsheet_data,
            ) for event in event_names
        }

        return season.SeasonInput(events=events)

    def _event_input(
        self,
        event_name: str,
        player_names: set[str],
        spreadsheet_data: season_spreadsheet.SeasonSheetReadData,
    ) -> season_event.EventInput:
        event_config = self.config.get_event_config(event_name)

        return season.EventInput(
            course=self._event_course_input(event_config),
            type=self._config_to_season_event_type(event_config.type),
            players=self._event_players_input(
                event_name=event_name, player_names=player_names, spreadsheet_data=spreadsheet_data
            ),
        )

    def _event_course_input(
        self,
        event_config: season_config.EventConfig,
    ) -> season_event.CourseInput:
        course_name = event_config.course_name
        tee_name = event_config.tee

        course_info = self.course_db.get_course(course_name)
        tee_info = course_info.get_tee_info(tee_name)

        return season_event.CourseInput(
            name=event_config.course_name,
            tee=season_event.CourseTeeData(
                name=tee_name,
                rating=tee_info.rating,
                slope=tee_info.slope
            ),
            hole_pars=season_event.CourseHolePars(course_info.hole_pars),
        )

    def _event_players_input(
        self,
        event_name: str,
        player_names: set[str],
        spreadsheet_data: season_spreadsheet.SeasonSheetReadData,
    ) -> dict[str, season_event.EventPlayerInput]:
        event_players: dict[str, season_event.EventPlayerInput] = {}

        for player_name in player_names:
            event_players[player_name] = season_event.EventPlayerInput(
                handicap_index=spreadsheet_data.players.player_handicaps[player_name][event_name],
                hole_scores=spreadsheet_data.events[event_name].player_scores[player_name],
            )

        return event_players

    def _config_to_season_event_type(self, config_event_type: season_config.EventType) -> season.EventType:
        match config_event_type:
            case season_config.EventType.STANDARD:
                return season.EventType.STANDARD

            case season_config.EventType.MAJOR:
                return season.EventType.MAJOR

            case _:
                # This should not be reachable unless new event types are introduced.
                raise ValueError(f"Unknown config event type: {config_event_type}")

    def _write_spreadsheet_data(self, season_results: season.SeasonResults) -> None:
        pass
