import dataclasses
import enum
import numpy as np
import pandas as pd
from typing import Dict, List

from sfsgt_scoring_2023 import course
from sfsgt_scoring_2023 import handicap
from sfsgt_scoring_2023 import player


class PlayerScoreHoleScoresException(Exception):
    """Exception to be raised by a PlayerScore when the hole scores series is malformed."""

class EventCombinedPointsException(Exception):
    """Exception to be raised by an Event  when the combined points data is malformed."""

class EventNoScoresSetException(Exception):
    """Exception to be raised by an Event if scores haven't been set before getting results."""

class EventPlayerScorecard:
    """Scorecard for a player in an event."""
    def __init__(self, hole_scores: Dict[int, int]) -> None:
        expected_holes = list(range(1, 19))

        if len(hole_scores) != 18 or list(hole_scores.keys()) != expected_holes:
            raise ValueError("Hole scores must have integer hole numbers 1-18 as keys.")

        if not all(
            isinstance(score, int) or (score is None)
            for score in hole_scores.values()
        ):
            raise ValueError("Hole scores must all be integer values or None.")

        self.hole_scores = hole_scores

    def is_valid(self) -> bool:
        return all(self.hole_scores.values())

    def strokes_out(self) -> int | None:
        if self.is_valid():
            return sum(list(self.hole_scores.values())[:9])

        return None

    def strokes_in(self) -> int | None:
        if self.is_valid():
            return sum(list(self.hole_scores.values())[9:])

        return None

    def gross_strokes(self) -> int | None:
        if self.is_valid():
            return sum(self.hole_scores.values())

        return None

    def net_strokes(self, course_handicap: int) -> int | None:
        if self.is_valid():
            gross_strokes = self.gross_strokes()
            assert gross_strokes is not None  # mypy

            return gross_strokes - course_handicap

        return None

    def scoring_differential(self, course_rating: float, course_slope: int) -> float | None:
        if self.is_valid():
            gross_strokes = self.gross_strokes()
            assert gross_strokes is not None  # mypy

            return handicap.calc_scoring_differential(
                total_score=gross_strokes,
                rating=course_rating,
                slope=course_slope,
            )

        return None



class EventScorecard:
    """Scorecards for all players in an event."""
    def __init__(self, player_scorecards: Dict[str, EventPlayerScorecard]) -> None:
        if not all(
            isinstance(scorecard, EventPlayerScorecard) for scorecard in player_scorecards.values()
        ):
            raise ValueError("All player scorecards must be EventPlayerScorecard type or None.")

        self.player_scorecards = player_scorecards

@dataclasses.dataclass(eq=True, frozen=True, kw_only=True)
class PlayerEventResult:
    """Event results for an individual player."""
    # Individual player data:
    # course_handicap: number of strokes a player is given against the course
    # strokes_out: gross score on holes 1-9
    # strokes_in: gross score on holes 10-18
    # gross_strokes: total gross score
    # net_strokes: gross score minus course handicap
    # scoring_differential: difference between a players score and the course rating, used
    #           to calculate the players handicap index
    #
    # Event player data:
    # gross_rank: player rank in the event based on gross score
    # net_rank: player rank in the event based on net score
    # gross_points: points earned by the player based on their gross score
    # net_points: points earned by the player based on their net score
    # event_points: combined gross/net points for the player
    # event_rank: player rank based on total event points
    course_handicap: int
    strokes_out: int | None
    strokes_in: int | None
    gross_strokes: int | None
    net_strokes: int | None
    scoring_differential: float | None
    gross_rank: int
    net_rank: int
    gross_points: float
    net_points: float
    event_points: float
    event_rank: float


class EventResult:
    """Results for all players in an event."""
    def __init__(self, player_results: Dict[str, PlayerEventResult]) -> None:
        if not all(isinstance(result, PlayerEventResult) for result in player_results.values()):
            raise ValueError("All player result value must be PlayerEventResult type.")

        self.player_results = player_results

    def full_results_df(self) -> pd.DataFrame:
        """Dataframe with the full set of results from the event.

        Player names are in the dataframe index.
        Column names match the attributes of PlayerEventResult
        """
        df = pd.DataFrame(
            {
                player_name: dataclasses.asdict(player_result)
                for player_name, player_result in self.player_results.items()
            }
        )
        # Transpose to get players names into index
        return df.transpose()

    def course_handicaps_df(self) -> pd.Series:
        return self.full_results_df().loc[:, "course_handicap"]

    def scoring_differentials_df(self) -> pd.Series:
        return self.full_results_df().loc[:, "scoring_differential"]


class PlayerScore:
    """Defines a score for an individual player in an event.
    """
    def __init__(
        self, course_handicap: int, hole_scores: pd.Series
    ) -> None:
        """Construct an instance of PlayerScore based on a player's course handicap and hole scores.

        Attributes:
            course_handicap: integer representing the players course handicap in this event
            hole_scores: pd.Series where the index is a hole number from 1 to 18 and the values
                are integers representing the score on that hole
        """
        self._front_nine_holes = [str(hole) for hole in range(1, 10)]
        self._back_nine_holes = [str(hole) for hole in range(10, 19)]

        expected_series_index = set(self._front_nine_holes + self._back_nine_holes)
        if not set(hole_scores.index) == expected_series_index:
            raise PlayerScoreHoleScoresException(
                "Malformed hole scores series. The index of the series should be strings 1 "
                f"through 18 representing hole numbers. Found {hole_scores.index}"
            )

        self.course_handicap = course_handicap
        self.hole_scores = hole_scores

    def get_results(self) -> pd.Series:
        """Returns a pandas series with results for an individual player.

        The returned Series will have the indices ["Out", "In", "Gross", "Net"], which represent
        the following:
            Out: Gross score on holes 1-9
            In: Gross score on holes 10-18
            Gross: Total gross score for the round
            Net: Gross score minus course handicap
        """
        # Index for the final series that is returned
        series_index = ["Out", "In", "Gross", "Net"]

        if not self.hole_scores.apply(isinstance, args=[int]).all():
            # If all values are not integers, then it's not a valid score.
            # Return a series full of NaN to indicate that
            return pd.Series(data=[np.nan, np.nan, np.nan, np.nan], index=series_index)

        front_nine_score = self.hole_scores.loc[self._front_nine_holes].sum()
        back_nine_score = self.hole_scores.loc[self._back_nine_holes].sum()
        gross_score = front_nine_score + back_nine_score
        net_score = gross_score - self.course_handicap

        data = [front_nine_score, back_nine_score, gross_score, net_score]

        return pd.Series(data=data, index=series_index)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PlayerScore):
            return (
                self.course_handicap == other.course_handicap and
                all(self.hole_scores == other.hole_scores)
            )

        return NotImplemented


class EventPointsCombinationMethod(enum.Enum):
    """Enum to define the method by which net and gross points will be combined."""

    # Points are combined as the sum of gross and net score points
    SUM = enum.auto()
    # Points are combined as the average of gross and net score points
    AVERAGE = enum.auto()
    # Points are combined with 60% net score points and 40% gross score points
    BLEND_60_PCT_NET = enum.auto()


class EventScoringConfig:
    """Scoring configuration for an event."""

    def __init__(
        self, points_by_rank: Dict[int, float], points_combo_method: EventPointsCombinationMethod
    ) -> None:
        """Instantiate class instance.

        Attributes:
            points_by_rank: Dictionary with points for each player rank in an event. Keys are
                ranks in an event and they must be strictly increasing from 1 to the maximum
                possible rank. Values are points for that rank in an event.
            points_combo_method: EventPointsCombinationMethod enum that defines the way that net and
                gross score points should be combined.

        Raises:
            ValueError: If the keys in points_by_rank do not start at 1 or are not strictly
                increaseing
        """
        ranks = list(points_by_rank.keys())
        ranks_are_strictly_increasing = all(np.diff(ranks) == 1)
        ranks_start_at_one = ranks[0] == 1
        if not (ranks_are_strictly_increasing and ranks_start_at_one):
            raise ValueError(
                "The keys in point_by_ranks must start at 1 and must be strictly increasing."
            )

        self.points_by_rank = points_by_rank
        self.points_combo_method = points_combo_method

    def __eq__(self, other: object) -> bool:
        """Equal comparison method for this class."""
        if isinstance(other, EventScoringConfig):
            return (
                self.points_by_rank == other.points_by_rank and
                self.points_combo_method == other.points_combo_method
            )
        else:
            return NotImplemented


class Event:
    """Defines an event with a group of players, a course, and a scoring config."""

    def __init__(
        self,
        players: player.PlayerGroup,
        course: course.Course,
        scoring_config: EventScoringConfig,
    ) -> None:
        """Construct an instance of Event based on players, course, and scoring config.

        Attributes:
            players: PlayerGroup object defining the players that are competing in an event.
            course: Course object defining the course that is being played in the event.
            scoring_config: EventScoringConfig object defining the way that the event should
                be scored.
        """
        self.course = course
        self.players = players
        self.scoring_config = scoring_config

        # Initialize an empty player scores dict
        self.player_scores: Dict[player.Player, PlayerScore] = {}

    def _player_course_handicap(self, player_name: str) -> int:
        """Calculate the integer course handicap for a single player on the event's course."""
        slope = self.course.slope
        rating = self.course.rating
        par = self.course.par
        player_handicap = self.players.get_player(player_name).handicap

        return handicap.calc_course_handicap(
            handicap_index=player_handicap,
            par=par,
            rating=rating,
            slope=slope,
        )

    def process_event(self, event_scorecard: EventScorecard) -> EventResult:
        """Process scorecards from an event and return the event results."""
        # calculate per-player data: course handicap, out, in, gross, net, scoring diff
        # calculate event data: gross rank, net rank, gross points, net points, event points, event rank
        # create per-player event result objects and return full-event result object
        player_event_data: Dict[str, Dict[str, int | float | None]] = {}
        for player_name, scorecard in event_scorecard.player_scorecards.items():
            course_handicap = handicap.calc_course_handicap(
                handicap_index=self.players.get_player(player_name).handicap,
                par=self.course.par,
                rating=self.course.rating,
                slope=self.course.slope
            )

            player_event_data[player_name] = {
                "course_handicap": course_handicap,
                "strokes_out": scorecard.strokes_out(),
                "strokes_in": scorecard.strokes_in(),
                "gross_strokes": scorecard.gross_strokes(),
                "net_strokes": scorecard.net_strokes(course_handicap=course_handicap),
                "scoring_differential": scorecard.scoring_differential(
                    course_rating=self.course.rating,
                    course_slope=self.course.slope,
                ),
            }

        # Set up an initial dataframe for calculating event-wide data
        # Transpose to place the player names as the index and dictionary keys as columns
        results_df = pd.DataFrame(player_event_data).transpose()

        results_df["gross_rank"] = results_df["gross_strokes"].rank(method="min", na_option="keep")
        results_df["net_rank"] = results_df["net_strokes"].rank(method="min", na_option="keep")

        gross_points_ser = self._points_ser(results_df["gross_rank"])
        gross_points_ser.name = "gross_points"
        results_df = results_df.join(gross_points_ser)

        net_points_ser = self._points_ser(results_df["net_rank"])
        net_points_ser.name = "net_points"
        results_df = results_df.join(net_points_ser)

        combined_points_ser = self._combined_points_ser(results_df[["gross_points", "net_points"]])
        combined_points_ser.name = "event_points"
        results_df = results_df.join(combined_points_ser)

        results_df["event_rank"] = results_df["event_points"].rank(method="min", ascending=False).astype(int)

        return EventResult(
            player_results={
                str(player_name): PlayerEventResult(**player_result_ser.to_dict())
                for player_name, player_result_ser in results_df.iterrows()
            }
        )

    def _points_ser(self, ranks_ser: pd.Series) -> pd.Series:
        """Calculates points for each player rank.

        If a rank is NaN, it indicates that there is no player score, so no points are awarded.

        For ties, the points for all ranks covered by the tie are split evently. For example, if
        3 players are tied for 2nd place, the points for 2nd, 3rd, and 4th are split evently and
        awarded to each player in the tie.

        Attributes:
            ranks_ser: pd.Series where the index is player names and values are player rank. Values
                are floats. If a value is NaN, it indicates that no play score has been reported.

        Returns:
            pd.Series where the index is player names and values are points for that player
        """
        # Make a copy so we don't edit the original object
        ranks = ranks_ser.copy()
        ranks.sort_values(inplace=True)

        # Initialize the points series with the same index as the ranks series
        points = pd.Series(data=[0.0] * ranks.size, index=ranks.index)

        if all(ranks.isna()):
            # If all of the ranks are NaN it means that no scores have been reported, return all
            # zeros for points
            return points

        else:
            # Iterate through each of the existing ranks in the input series so that ties can
            # be processed
            min_rank = int(ranks.min())
            max_rank = int(ranks.max())
            for rank in range(min_rank, max_rank + 1):
                players_in_rank = ranks[ranks == rank]
                num_players = players_in_rank.size

                # No ties. Points are awarded
                if num_players == 1:
                    player_name = players_in_rank.index[0]
                    points[player_name] = self._points_for_rank(rank)

                # 1 or more players are tied. Points for all ranks in the tie are split evenly to
                # those players.
                elif num_players > 1:
                    ranks_in_tie = list(range(rank, rank + num_players))
                    points_in_tie = [self._points_for_rank(tie_rank) for tie_rank in ranks_in_tie]

                    average_points_for_tie = np.mean(points_in_tie)

                    for player_name in players_in_rank.index:
                        points[player_name] = average_points_for_tie

                else:
                    continue

            return points

    def _points_for_rank(self, rank: int) -> float:
        """Points for a specific rank, based on the scoring config."""
        return self.scoring_config.points_by_rank[rank]

    def _combined_points_ser(self, points_df: pd.DataFrame) -> pd.Series:
        """Calculate the combined points for each player based on the scoring config method.

        Attributes:
            points_df: pd.DataFrame with gross and net points for each player. The dataframe
                index should be player names. The column labels must be
                ["gross_points", "net_points"]. The values are floats representing the players
                gross and net score respectively.

        Returns:
            pd.Series with combined points for each player. The index is player names. Values are
                floats with the combined points for each player.

        Raises:
            ValueError: if the points_df does not have the columns "gross_points" an "net_points"
        """
        if not set(points_df.columns) == {"gross_points", "net_points"}:
            raise EventCombinedPointsException(
                "Expected points_df to have column labels 'gross_points' and 'net_points', "
                f"found {points_df.columns}"
            )

        match self.scoring_config.points_combo_method:
            case EventPointsCombinationMethod.SUM:
                return points_df["gross_points"] + points_df["net_points"]

            case EventPointsCombinationMethod.AVERAGE:
                return points_df.mean(axis=1)

            case EventPointsCombinationMethod.BLEND_60_PCT_NET:
                return 0.4 * points_df["gross_points"] + 0.6 * points_df["net_points"]
