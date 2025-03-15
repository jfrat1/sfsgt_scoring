from typing import NamedTuple

import courses
import season_config
from season_common import player
from sfsgt_scoring import season
from sfsgt_scoring.season import (
    event as season_event,
)
from sfsgt_scoring.spreadsheet import season as season_spreadsheet


# TODO: The finale stuff belong somewhere else, but it's here for now so we
# can get handicaps for the finale
class FinaleHandicap(NamedTuple):
    ghin_handicap: float
    season_handicap: float
    finale_handicap: float
    # TODO: This really needs to not be hard-coded to Corica
    corica_finale_course_handicap: int


class FinaleHandicaps(dict[str, FinaleHandicap]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class FinaleHandicapCalculator:
    def __init__(
        self,
        spreadsheet_data: season_spreadsheet.SeasonSheetReadData,
        season_results: season.SeasonResults,
    ) -> None:
        self._player_names = spreadsheet_data.player_names()
        self._player_handicaps = spreadsheet_data.players.player_handicaps
        self._season_results = season_results

    def finale_handicaps(self) -> FinaleHandicaps:
        ghin_handicaps = self._ghin_handicaps()
        season_handicaps = self._season_handicaps()
        return self._finale_handicaps(
            ghin_handicaps=ghin_handicaps,
            season_handicaps=season_handicaps,
        )

    def _ghin_handicaps(self) -> dict[str, float]:
        ghin_handicaps: dict[str, float] = {}
        for player_ in self._player_names:
            ghin_handicaps[player_] = self._player_handicaps[player_]["FINALE"]

        return ghin_handicaps

    def _season_handicaps(self) -> dict[str, float]:
        season_handicaps: dict[str, float] = {}
        for player_ in self._player_names:
            season_handicaps[player_] = self._season_results.cumulative.players[player_].season_handicap

        return season_handicaps

    def _finale_handicaps(
        self,
        ghin_handicaps: dict[str, float],
        season_handicaps: dict[str, float],
    ) -> FinaleHandicaps:
        finale_handicaps: dict[str, FinaleHandicap] = {}
        for player_ in self._player_names:
            finale_handicaps[player_] = self._finale_player_handicap(
                ghin_handicap=ghin_handicaps[player_],
                season_handicap=season_handicaps[player_],
            )

        return FinaleHandicaps(finale_handicaps)

    def _finale_player_handicap(
        self,
        ghin_handicap: float,
        season_handicap: float,
    ) -> FinaleHandicap:
        MIN_GHIN_RATIO = 0.95
        MAX_GHIN_RATIO = 1.05
        MAX_STROKE_OFFSET = 0.5
        MAX_FINALE_HANDICAP = 19.0

        min_finale_handicap = min(
            ghin_handicap * MIN_GHIN_RATIO,
            ghin_handicap - MAX_STROKE_OFFSET,
        )
        max_finale_handicap = max(
            ghin_handicap * MAX_GHIN_RATIO,
            ghin_handicap + MAX_STROKE_OFFSET,
        )

        # Target a 50/50 split of GHIN and season handicap
        target_finale_handicap = (ghin_handicap + season_handicap) / 2

        # Limit that to bounds around the GHIN handicap
        ghin_bounded_finale_handicap = min(max(target_finale_handicap, min_finale_handicap), max_finale_handicap)

        # Cap that to a max overall handicap
        capped_finale_handicap = min(ghin_bounded_finale_handicap, MAX_FINALE_HANDICAP)

        # Round to 1 decimal place
        finale_handicap = round(capped_finale_handicap, 1)

        return FinaleHandicap(
            ghin_handicap=ghin_handicap,
            season_handicap=season_handicap,
            finale_handicap=finale_handicap,
            corica_finale_course_handicap=self.course_handicap(finale_handicap),
        )

    def course_handicap(self, handicap_index: float) -> int:
        slope = 123
        rating = 70.4
        strokes_for_par = 72

        course_handicap_raw = handicap_index * (slope / 113) + (rating - strokes_for_par)
        course_handicap = round(course_handicap_raw, 0)

        return int(course_handicap)


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
        course_provider: courses.CourseProvider,
    ) -> None:
        self.config = config
        self.sheet = sheet
        self.course_provider = course_provider

        self._configure_season_sheet()

    def _configure_season_sheet(self) -> None:
        event_configs = self._season_sheet_event_configs()
        sheet_config = self._season_sheet_config(event_configs)
        self.sheet.configure(sheet_config)

    def _season_sheet_event_configs(self) -> dict[str, season_spreadsheet.SeasonSheetEventConfig]:
        return {
            event_config.event_name: season_spreadsheet.SeasonSheetEventConfig(
                event_num=event_num,
                sheet_name=event_config.sheet_name,
                scorecard_start_cell=event_config.scorecard_sheet_start_cell,
            )
            for event_num, event_config in self.config.event_configs().items()
        }

    def _season_sheet_config(
        self, event_configs: dict[str, season_spreadsheet.SeasonSheetEventConfig]
    ) -> season_spreadsheet.SeasonSheetConfig:
        return season_spreadsheet.SeasonSheetConfig(
            sheet_id=self.config.sheet_id,
            leaderboard_sheet_name=self.config.leaderboard_sheet_name,
            players_sheet_name=self.config.players_sheet_name,
            events=event_configs,
            is_finale_enabled=self.config.finale_handicaps_sheet.enabled,
            finale_handicaps_sheet_name=self.config.finale_handicaps_sheet.sheet_name,
        )

    def run(self) -> None:
        sheet_read_data = self._read_spreadsheet_data()
        season = self._create_season(spreadsheet_data=sheet_read_data)
        season_results = season.results()

        finale_handicaps = FinaleHandicapCalculator(
            spreadsheet_data=sheet_read_data,
            season_results=season_results,
        ).finale_handicaps()

        self._write_spreadsheet_data(season_results=season_results, finale_handicaps=finale_handicaps)

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
            )
            for event in event_names
        }

        return season.SeasonInput(events=events, player_names=player_names)

    def _event_input(
        self,
        event_name: str,
        player_names: list[str],
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
        # TODO: This rendition of the app assumes that there's only 1 tee.
        # We default to the mens tee for now, but a refactor is underway.
        tee_name = event_config.tees.mens_tee

        course_info = self.course_provider.get_course(course_name)
        tee_info = course_info.get_tee_info(tee_name=tee_name, player_gender=player.PlayerGender.MALE)

        return season_event.CourseInput(
            name=event_config.course_name,
            tee=season_event.CourseTeeData(name=tee_name, rating=tee_info.rating, slope=tee_info.slope),
            hole_pars=season_event.CourseHolePars(course_info.hole_pars),
        )

    def _event_players_input(
        self,
        event_name: str,
        player_names: list[str],
        spreadsheet_data: season_spreadsheet.SeasonSheetReadData,
    ) -> dict[str, season_event.EventPlayerInput]:
        event_players: dict[str, season_event.EventPlayerInput] = {}

        for player_name in player_names:
            handicap_index = spreadsheet_data.players.player_handicaps[player_name][event_name]
            hole_scores = self._event_player_hole_scores_input(
                spreadsheet_data.events[event_name].player_scores[player_name]
            )

            event_players[player_name] = season_event.EventPlayerInput(
                handicap_index=handicap_index,
                scorecard=hole_scores,
            )

        return event_players

    def _event_player_hole_scores_input(
        self,
        hole_scores_sheet_data: season_spreadsheet.worksheet.IHoleScores,
    ) -> season_event.IScorecard:
        if isinstance(hole_scores_sheet_data, season_spreadsheet.worksheet.IncompleteScore):
            return season.event.IncompleteScorecard()
        else:
            return season.event.Scorecard(strokes_per_hole=hole_scores_sheet_data.scores())

    def _config_to_season_event_type(self, config_event_type: season_config.EventType) -> season.EventType:
        match config_event_type:
            case season_config.EventType.STANDARD:
                return season.EventType.STANDARD

            case season_config.EventType.MAJOR:
                return season.EventType.MAJOR

            case _:
                # This should not be reachable unless new event types are introduced.
                raise ValueError(f"Unknown config event type: {config_event_type}")

    def _write_spreadsheet_data(
        self,
        season_results: season.SeasonResults,
        finale_handicaps: FinaleHandicaps,
    ) -> None:
        write_data = self._generate_spreadsheet_write_data(
            season_results=season_results, finale_handicaps=finale_handicaps
        )
        self.sheet.write(data=write_data)

    def _generate_spreadsheet_write_data(
        self,
        season_results: season.SeasonResults,
        finale_handicaps: FinaleHandicaps,
    ) -> season_spreadsheet.SeasonSheetWriteData:
        leaderboard_write_data = self._generate_spreadsheet_leaderboard_write_data(season_results)
        events_write_data = self._generate_spreadsheet_events_write_data(season_results)
        finale_handicaps_write_data = self._generate_spreadsheet_finale_handicaps_write_data(finale_handicaps)

        return season_spreadsheet.SeasonSheetWriteData(
            leaderboard=leaderboard_write_data,
            events=events_write_data,
            finale_handicaps=finale_handicaps_write_data,
        )

    def _generate_spreadsheet_leaderboard_write_data(
        self,
        season_results: season.SeasonResults,
    ) -> season_spreadsheet.worksheet.LeaderboardWriteData:
        leaderboard_players: list[season_spreadsheet.worksheet.PlayerLeaderboardWriteData] = []
        for player_name, cumulative_player_data in season_results.cumulative.players.items():
            player_event_points = {
                event_name: event_data.players[player_name].event_points
                for event_name, event_data in season_results.events.items()
            }
            leaderboard_player = season_spreadsheet.worksheet.PlayerLeaderboardWriteData(
                player_name=player_name,
                season_points=cumulative_player_data.season_points,
                season_rank=int(cumulative_player_data.season_rank),
                events_played=cumulative_player_data.num_events_completed,
                birdies=cumulative_player_data.num_birdies,
                eagles=cumulative_player_data.num_eagles,
                net_strokes_wins=cumulative_player_data.num_net_strokes_wins,
                net_strokes_top_fives=cumulative_player_data.num_net_strokes_top_fives,
                net_strokes_top_tens=cumulative_player_data.num_net_strokes_top_tens,
                event_wins=cumulative_player_data.num_event_wins,
                event_top_fives=cumulative_player_data.num_event_top_fives,
                event_top_tens=cumulative_player_data.num_event_top_tens,
                event_points=player_event_points,
            )
            leaderboard_players.append(leaderboard_player)

        return season_spreadsheet.worksheet.LeaderboardWriteData(players=leaderboard_players)

    def _generate_spreadsheet_events_write_data(
        self,
        season_results: season.SeasonResults,
    ) -> season_spreadsheet.SeasonEventsWriteData:
        return {
            event_name: self._generate_spreadsheet_event_write_data(event_data)
            for event_name, event_data in season_results.events.items()
        }

    def _generate_spreadsheet_event_write_data(
        self,
        event_results: season_event.EventResult,
    ) -> season_spreadsheet.worksheet.EventWriteData:
        event_players_write_data: dict[str, season_spreadsheet.worksheet.PlayerEventWriteData] = {}
        for player_name, player_result in event_results.players.items():
            if player_result.is_complete_result():
                event_players_write_data[player_name] = season_spreadsheet.worksheet.PlayerEventWriteData(
                    front_9_strokes=player_result.front_9_gross,
                    back_9_strokes=player_result.back_9_gross,
                    gross_strokes=player_result.total_gross,
                    course_handicap=player_result.course_handicap,
                    net_strokes=player_result.total_net,
                    gross_rank=int(player_result.gross_score_rank),
                    net_rank=int(player_result.net_score_rank),
                    gross_points=player_result.gross_score_points,
                    net_points=player_result.net_score_points,
                    event_points=player_result.event_points,
                    event_rank=int(player_result.event_rank),
                )
            else:
                # TODO: I'm not a fan of the season runner needing to know something special about
                # what to write into event sheet when a player has an incomplete score.
                # Consider better ways to abstract this behavior into a no-result for the individual
                # results.
                event_players_write_data[player_name] = season_spreadsheet.worksheet.PlayerEventWriteData(
                    front_9_strokes="",  # type: ignore # Will be fixed with better abstraction at this level.
                    back_9_strokes="",  # type: ignore # Will be fixed with better abstraction at this level.
                    gross_strokes="",  # type: ignore # Will be fixed with better abstraction at this level.
                    course_handicap="",  # type: ignore # Will be fixed with better abstraction at this level.
                    net_strokes="",  # type: ignore # Will be fixed with better abstraction at this level.
                    gross_rank="N/A",  # type: ignore # Will be fixed with better abstraction at this level.
                    net_rank="N/A",  # type: ignore # Will be fixed with better abstraction at this level.
                    gross_points=player_result.gross_score_points,
                    net_points=player_result.net_score_points,
                    event_points=player_result.event_points,
                    event_rank=int(player_result.event_rank),
                )

        return season_spreadsheet.worksheet.EventWriteData(
            players=event_players_write_data,
            birdies=[],
            eagles=[],
            hole_scores_over_max=[],
        )

    def _generate_spreadsheet_finale_handicaps_write_data(
        self,
        finale_handicaps: FinaleHandicaps,
    ) -> season_spreadsheet.worksheet.FinaleHandicapsWriteData:
        sheet_finale_handicaps: dict[str, season_spreadsheet.worksheet.FinaleHandicap] = {}
        for player, player_handicap in finale_handicaps.items():
            sheet_finale_handicaps[player] = season_spreadsheet.worksheet.FinaleHandicap(
                ghin_handicap=player_handicap.ghin_handicap,
                season_handicap=player_handicap.season_handicap,
                finale_handicap=player_handicap.finale_handicap,
                finale_course_handicap=player_handicap.corica_finale_course_handicap,
            )

        return season_spreadsheet.worksheet.FinaleHandicapsWriteData(sheet_finale_handicaps)
