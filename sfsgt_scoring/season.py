
import collections
import dataclasses
import pandas as pd
import string
from typing import Dict, List

from sfsgt_scoring import (
    event,
    player,
    season_sheet,
)


@dataclasses.dataclass(eq=True, frozen=True)
class SeasonEventConfig:
    # String value for the course name
    course_name: str
    # String value for the scorecard sheet name - this is the sheet where data is read from
    scorecard_sheet_name: str
    # String value for the points sheet name - this is the sheet where event results are written
    results_sheet_name: str
    # Dict with points that each player should receive for a given rank in the event
    points_by_rank: Dict[int, float]

class SeasonPlayer:
    def __init__(self, name: str, handicap_by_event: Dict[str, float]) -> None:
        self.name = name
        self.handicap_by_event = handicap_by_event

    def event_handicap(self, event_name: str) -> float:
        if event_name not in self.handicap_by_event.keys():
            raise KeyError(
                f"Can't find event {event_name} in handicaps for player {self.name}"
            )

        return self.handicap_by_event[event_name]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SeasonPlayer):
            return (
                self.name == other.name
                and self.handicap_by_event == other.handicap_by_event
            )

        else:
            return NotImplemented

class SeasonPlayerGroup:
    def __init__(self, player_list: List[SeasonPlayer]) -> None:
        self.player_list = player_list

    def get_event_player_group(self, event_name: str) -> player.PlayerGroup:
        """Get a PlayerGroup for an event in a season."""
        return player.PlayerGroup(
            player_list=[
                player.Player(
                    name=player_.name,
                    handicap=player_.event_handicap(event_name)
                ) for player_ in self.player_list
            ]
        )

    def player_names(self) -> List[str]:
        return [player.name for player in self.player_list]

class Season:
    def __init__(
        self, season_sheet: season_sheet.SeasonSheet, event_configs: List[SeasonEventConfig]
    ) -> None:
        self.sheet = season_sheet
        self.event_configs = event_configs

        # Old way of loading a single handicap for the entire season
        # Remove once we think it's not needed anymore
        # self.players = season_sheet.read_players_sheet()

        self.courses = season_sheet.read_courses_sheet()
        self.players = season_sheet.read_player_handicaps_sheet(
            expected_events=self.courses.course_names(),
        )

        self._events: List[event.Event] = []
        self._event_scorecards: Dict[str, event.EventScorecard] = {}
        self._event_results: Dict[str, event.EventResult] = {}

        # Initialize a zeros dataframe for season points
        self.season_points = pd.DataFrame(
            data=0,
            index=self.players.player_names(),
            columns=[event_config.course_name for event_config in event_configs],
        )

    def process_event(self, event_config: SeasonEventConfig) -> None:
        event_ = event.Event(
            # Get player data for this event specifically . Player handicaps can vary for
            # each event in the season.
            players=self.players.get_event_player_group(event_config.course_name),
            course=self.courses.get_course(event_config.course_name),
            scoring_config=event.EventScoringConfig(
                points_by_rank=event_config.points_by_rank,
                points_combo_method=event.EventPointsCombinationMethod.SUM,
            ),
        )

        event_scorecard = self.sheet.read_event_scorecard_sheet(
            worksheet_name=event_config.scorecard_sheet_name,
            expected_players=self.players.player_names(),
        )
        event_result = event_.process_event(event_scorecard=event_scorecard)
        event_result_df = event_result.full_results_df()

        # Record points for this event in the season points dataframe
        points = event_result_df["event_points"]
        self.season_points.loc[:, event_.course.course_name] = points

        event_result_df.columns = [
            string.capwords(col_label.replace("_", " "))
            for col_label in event_result_df.columns
        ]
        self.sheet.write_event_results(
            worksheet_name=event_config.results_sheet_name,
            results_df=event_result_df,
        )

        self._events.append(event_)
        self._event_scorecards[event_config.course_name] = event_scorecard
        self._event_results[event_config.course_name] = event_result

    def process_all_events(self) -> None:
        for event_config in self.event_configs:
            self.process_event(event_config)

    def course_handicaps_df(self) -> pd.DataFrame:
        event_course_handicaps: List[pd.DataFrame] = []
        for event_name, event_result in self._event_results.items():
            course_handicap_df = event_result.course_handicaps_df()
            course_handicap_df.name = event_name
            event_course_handicaps.append(course_handicap_df)

        df = pd.concat(event_course_handicaps, axis=1)
        # Promote the player-name index to be a column in the dataframe
        df.reset_index(inplace=True, names=["Player"])

        return df

    def write_course_handicaps(self) -> None:
        self.sheet.write_course_handicaps(self.course_handicaps_df())

    def write_leaderboard(self) -> None:
        leaderboard_df = self.season_points.copy()
        original_columns = leaderboard_df.columns

        leaderboard_df["Total"] = leaderboard_df.sum(axis=1)
        # Round the points data to 1 decimal place before adding rank column
        leaderboard_df = leaderboard_df.round(1)

        leaderboard_df["Rank"] = leaderboard_df["Total"].rank(method="min", ascending=False)

        # Set the column order to have Rank and Total Points before the individual event points
        final_columns = ["Rank", "Total"]
        final_columns.extend(original_columns)
        leaderboard_df = leaderboard_df.loc[:, final_columns]

        leaderboard_df.sort_values(by="Rank", inplace=True)
        leaderboard_df.reset_index(names=["Player"], inplace=True)

        self.sheet.write_leaderboard(leaderboard_df=leaderboard_df)

    def event_scoring_differentials(self) -> pd.DataFrame:
        # This dataframe has player names as the index and event names as the column headers
        # scoring differentials for each player / event are the values
        # if a player did not post a score for an event, the value will be NaN

        event_scoring_diffs: List[pd.DataFrame] = []
        for event_name, event_result in self._event_results.items():
            scoring_diff_df = event_result.scoring_differentials_df()
            scoring_diff_df.name = event_name
            event_scoring_diffs.append(scoring_diff_df)

        return pd.concat(event_scoring_diffs, axis=1)

    def season_finale_player_handicaps(self) -> pd.DataFrame:
        """Returned dataframe has:
        * player names as index
        * the following columns headers:
          * Rounds Played
          * Handicap Before Adjustment
          * Panalty
          * Finale Handicap
        """
        HandicapParams = collections.namedtuple(
            "HandicapParams",
            ["num_rounds_for_avg", "penalty_strokes"]
        )
        handicap_calc_params_by_rounds_played = {
            1: HandicapParams(num_rounds_for_avg=1, penalty_strokes=2.0),
            2: HandicapParams(num_rounds_for_avg=1, penalty_strokes=1.5),
            3: HandicapParams(num_rounds_for_avg=2, penalty_strokes=1.0),
            4: HandicapParams(num_rounds_for_avg=2, penalty_strokes=0.5),
            5: HandicapParams(num_rounds_for_avg=3, penalty_strokes=0),
        }

        scoring_diffs = self.event_scoring_differentials()

        season_finale_handicaps_df = pd.DataFrame(
            data="No rounds played",
            index=self.players.player_names(),
            columns=[
                "Rounds Played", "Handicap Before Adjustment", "Penalty", "Finale Handicap"
            ],
        )
        for player_name, player_scoring_diffs in scoring_diffs.iterrows():

            rounds_played = player_scoring_diffs.count()
            if rounds_played > 0:
                handicap_calc_params = handicap_calc_params_by_rounds_played[rounds_played]
                player_scoring_diffs_sorted = player_scoring_diffs.sort_values()

                # Mean of the N lowest handicaps from the season
                scoring_diffs_for_handicap = player_scoring_diffs_sorted[
                    :handicap_calc_params.num_rounds_for_avg
                ]
                handicap_before_adjustment = scoring_diffs_for_handicap.mean()

                season_handicap = handicap_before_adjustment - handicap_calc_params.penalty_strokes

                # Fill the dataframe
                season_finale_handicaps_df.loc[player_name, "Rounds Played"] = int(rounds_played)
                season_finale_handicaps_df.loc[
                    player_name, "Handicap Before Adjustment"
                ] = round(handicap_before_adjustment, 1)
                season_finale_handicaps_df.loc[
                    player_name, "Penalty"
                ] = handicap_calc_params.penalty_strokes
                season_finale_handicaps_df.loc[
                    player_name, "Finale Handicap"
                ] = round(season_handicap, 1)

        season_finale_handicaps_df.reset_index(names=["Players"], inplace=True)
        return season_finale_handicaps_df

