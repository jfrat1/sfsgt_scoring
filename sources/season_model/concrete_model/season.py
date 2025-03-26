from season_common.rank import RankManager, RankOrder, RankValue
from season_model.api.input import SeasonModelInput
from season_model.api.model import SeasonModel
from season_model.api.result import (
    SeasonModelEventResult,
    SeasonModelOverallResults,
    SeasonModelPlayerOverallResult,
    SeasonModelResults,
)
from season_model.concrete_model.event import EventResultGenerator


class ConcreteSeasonModel(SeasonModel):
    def calculate_results(self, input: SeasonModelInput) -> SeasonModelResults:
        player_names = input.player_names
        event_names = input.event_names

        event_results: dict[str, SeasonModelEventResult] = {}
        for event in event_names:
            event_input = input.event_input(event_name=event)
            event_results[event] = EventResultGenerator(input=event_input).generate()

        overall_results = SeasonOverallResultsGenerator(
            player_names=player_names,
            event_results=event_results,
        ).generate()

        return SeasonModelResults(
            events=list(event_results.values()),
            overall=overall_results,
        )


class SeasonOverallResultsGenerator:
    def __init__(
        self,
        player_names: list[str],
        event_results: dict[str, SeasonModelEventResult],
    ) -> None:
        self._player_names = player_names
        self._event_results = event_results

    def generate(self) -> SeasonModelOverallResults:
        overall_player_results = self._unranked_overall_results(self._event_results)
        player_season_ranks = self._player_season_ranks(overall_player_results)

        for player_name, player_rank in player_season_ranks.items():
            overall_player_results[player_name].set_season_rank(player_rank)

        return SeasonModelOverallResults(players=list(overall_player_results.values()))

    def _unranked_overall_results(
        self,
        event_results: dict[str, SeasonModelEventResult],
    ) -> dict[str, SeasonModelPlayerOverallResult]:
        overall_player_results: dict[str, SeasonModelPlayerOverallResult] = {}
        for player_name in self._player_names:
            overall_player_results[player_name] = self._player_overall_results(
                event_results=event_results,
                player_name=player_name,
            )

        return overall_player_results

    def _player_overall_results(
        self,
        event_results: dict[str, SeasonModelEventResult],
        player_name: str,
    ) -> SeasonModelPlayerOverallResult:
        season_points = 0.0
        num_birdies = 0
        num_eagles = 0
        num_albatrosses = 0
        num_events_completed = 0
        num_net_strokes_wins = 0
        num_net_strokes_top_fives = 0
        num_net_strokes_top_tens = 0
        num_event_wins = 0
        num_event_top_fives = 0
        num_event_top_tens = 0

        score_differentials: list[float] = []

        for event_result in event_results.values():
            player_event_results = event_result.player_result(player_name)

            season_points += player_event_results.event_points
            num_birdies += player_event_results.num_birdies
            num_eagles += player_event_results.num_eagles
            num_albatrosses += player_event_results.num_albatrosses

            if player_event_results.is_complete_result:
                num_events_completed += 1
                score_differentials.append(player_event_results.score_differential)

                num_net_strokes_wins += 1 if player_event_results.net_score_rank.is_win() else 0
                num_net_strokes_top_fives += 1 if player_event_results.net_score_rank.is_top_five() else 0
                num_net_strokes_top_tens += 1 if player_event_results.net_score_rank.is_top_ten() else 0

                num_event_wins += 1 if player_event_results.event_rank.is_win() else 0
                num_event_top_fives += 1 if player_event_results.event_rank.is_top_five() else 0
                num_event_top_tens += 1 if player_event_results.event_rank.is_top_ten() else 0

        season_handicap = SeasonHandicapCalculator(score_differentials=score_differentials).calculate()

        return SeasonModelPlayerOverallResult(
            name=player_name,
            season_points=season_points,
            num_birdies=num_birdies,
            num_eagles=num_eagles,
            num_albatrosses=num_albatrosses,
            num_events_completed=num_events_completed,
            num_net_strokes_wins=num_net_strokes_wins,
            num_net_strokes_top_fives=num_net_strokes_top_fives,
            num_net_strokes_top_tens=num_net_strokes_top_tens,
            num_event_wins=num_event_wins,
            num_event_top_fives=num_event_top_fives,
            num_event_top_tens=num_event_top_tens,
            season_handicap=season_handicap,
        )

    def _player_season_ranks(
        self,
        cumulative_player_results: dict[str, SeasonModelPlayerOverallResult],
    ) -> dict[str, RankValue]:
        rank_manager = RankManager()
        player_season_points = {
            player_name: player_result.season_points for player_name, player_result in cumulative_player_results.items()
        }
        player_season_ranks = rank_manager.player_ranks_from_values(
            player_values=player_season_points,
            rank_order=RankOrder.DESCENDING,
        )

        return player_season_ranks


class SeasonHandicapCalculator:
    def __init__(self, score_differentials: list[float]) -> None:
        self._score_differentials = score_differentials

    def calculate(self) -> float:
        score_differentials = sorted(self._score_differentials)
        num_rounds = len(score_differentials)

        base_season_handicap = self.calc_base_season_handicap(
            score_differentials_sorted=score_differentials,
            num_rounds=num_rounds,
        )
        handicap_penalty = self.calc_season_handicap_penalty(num_rounds=num_rounds)

        return base_season_handicap - handicap_penalty

    def calc_base_season_handicap(self, score_differentials_sorted: list[float], num_rounds: int) -> float:
        match num_rounds:
            case 0:
                return 0.0
            case 1 | 2 | 3:
                # Lowest 1 round used for season handicap
                return round(score_differentials_sorted[0], 1)
            case 4 | 5:
                # Lowest 2 rounds used for season handicap
                return round(sum(score_differentials_sorted[0:2]) / 2, 1)
            case 6:
                # Lowest 3 rounds used for season handicap
                return round(sum(score_differentials_sorted[0:3]) / 3, 1)
            case _:
                return 0.0

    def calc_season_handicap_penalty(self, num_rounds: int) -> float:
        match num_rounds:
            case 1:
                return 1.0
            case 2:
                return 0.5
            case _:
                return 0.0
