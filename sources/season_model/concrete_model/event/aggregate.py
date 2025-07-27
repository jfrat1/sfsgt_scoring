from typing import TypeVar

from season_common.rank import NoRankValue, Rank, RankManager, RankOrder, RankValue

from season_model.api.input import SeasonModelEventType
from season_model.api.result import (
    SeasonModelCompleteEventPlayerIndividualResult,
    SeasonModelEventPlayerAggregateResult,
    SeasonModelEventPlayerIndividualResult,
    SeasonModelIncompleteEventPlayerInividualResult,
)
from season_model.concrete_model.event.points import Points

T = TypeVar("T")


class EventAggregateResultsError(Exception):
    pass


class EventAggregateResultsGenerator:
    def __init__(
        self,
        individual_results: dict[str, SeasonModelEventPlayerIndividualResult],
        event_type: SeasonModelEventType,
    ) -> None:
        self._complete_results = self._filter_results_with_class_type(
            player_results=individual_results,
            class_type=SeasonModelCompleteEventPlayerIndividualResult,
        )
        self._incomplete_results = self._filter_results_with_class_type(
            player_results=individual_results,
            class_type=SeasonModelIncompleteEventPlayerInividualResult,
        )

        self._verify_grouping_of_results(player_names=list(individual_results.keys()))

        self._rank_manager = RankManager()
        self._points_manager = Points(event_type)

    def _filter_results_with_class_type(
        self,
        player_results: dict[str, SeasonModelEventPlayerIndividualResult],
        class_type: type[T],
    ) -> dict[str, T]:
        return {player_name: result for player_name, result in player_results.items() if isinstance(result, class_type)}

    def _verify_grouping_of_results(self, player_names: list[str]) -> None:
        grouped_player_names = set(self._complete_results.keys()).union(set(self._incomplete_results.keys()))

        if grouped_player_names != set(player_names):
            # This should not be reachable, but it's best to prove that theory.
            raise EventAggregateResultsError(
                "Player inividual results could not be grouped into complete and incomlpete results."
            )

    def generate(self) -> dict[str, SeasonModelEventPlayerAggregateResult]:
        cumulative_complete_results = self._aggregate_results_from_complete_individual_results()
        highest_event_rank = self._highest_complete_results_rank(cumulative_complete_results)

        cumulative_incomplete_results = self._aggregate_results_from_incomplete_individual_results(
            highest_event_rank_from_complete_results=highest_event_rank,
        )

        return cumulative_complete_results | cumulative_incomplete_results

    def _aggregate_results_from_complete_individual_results(
        self,
    ) -> dict[str, SeasonModelEventPlayerAggregateResult]:
        complete_results = self._complete_results
        player_names = complete_results.keys()

        # TODO: this whole thing feels messy to me
        gross_score_ranks = self._rank_manager.player_ranks_from_values(
            player_values={name: result.total_gross for name, result in self._complete_results.items()},
            rank_order=RankOrder.ASCENDING,
        )
        net_score_ranks = self._rank_manager.player_ranks_from_values(
            player_values={name: result.total_net for name, result in self._complete_results.items()},
            rank_order=RankOrder.ASCENDING,
        )
        gross_score_points = self._points_manager.player_points_from_ranks(
            player_ranks={name: int(rank_) for name, rank_ in gross_score_ranks.items()}
        )
        net_score_points = self._points_manager.player_points_from_ranks(
            player_ranks={name: int(rank_) for name, rank_ in net_score_ranks.items()}
        )
        event_points = {name: gross_score_points[name] + net_score_points[name] for name in player_names}
        event_ranks = self._rank_manager.player_ranks_from_values(
            player_values=event_points,
            rank_order=RankOrder.DESCENDING,
        )

        result: dict[str, SeasonModelEventPlayerAggregateResult] = {}
        for name in player_names:
            result[name] = SeasonModelEventPlayerAggregateResult(
                gross_score_points=gross_score_points[name],
                net_score_points=net_score_points[name],
                event_points=event_points[name],
                gross_score_rank=gross_score_ranks[name],
                net_score_rank=net_score_ranks[name],
                event_rank=event_ranks[name],
            )

        return result

    def _highest_complete_results_rank(
        self, cumulative_complete_results: dict[str, SeasonModelEventPlayerAggregateResult]
    ) -> Rank:
        is_results_dict_empty = len(cumulative_complete_results) == 0
        if is_results_dict_empty:
            return NoRankValue()

        return max(result.event_rank for result in cumulative_complete_results.values())

    def _aggregate_results_from_incomplete_individual_results(
        self,
        highest_event_rank_from_complete_results: Rank,
    ) -> dict[str, SeasonModelEventPlayerAggregateResult]:
        incomplete_results = self._incomplete_results

        event_rank_for_all_incomplete_results = self._event_rank_for_all_incomplete_results(
            highest_event_rank_from_complete_results
        )

        return {
            name: SeasonModelEventPlayerAggregateResult(
                gross_score_points=0.0,
                net_score_points=0.0,
                event_points=0.0,
                gross_score_rank=NoRankValue(),
                net_score_rank=NoRankValue(),
                event_rank=event_rank_for_all_incomplete_results,
            )
            for name in incomplete_results.keys()
        }

    def _event_rank_for_all_incomplete_results(
        self,
        highest_event_rank_from_complete_results: Rank,
    ) -> RankValue:
        if isinstance(highest_event_rank_from_complete_results, NoRankValue):
            return RankValue(1)

        else:
            return highest_event_rank_from_complete_results + 1
