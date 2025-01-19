from typing import TypeVar

from .. import rank
from . import course, inputs, player, points, results


class EventProcessingError(Exception):
    """Exception to be raised when a processing error is encountered by an event."""


class Event:
    def __init__(self, input: inputs.EventInput) -> None:
        self._input = input

        course_ = course.Course(input.course)
        self._players = self._create_players(course_)

    def _create_players(self, course_: course.Course) -> dict[str, player.EventPlayer]:
        return {
            player_name: player.EventPlayer(input=player_input, course_=course_)
            for player_name, player_input in self._input.players.items()
        }

    def result(self) -> results.EventResult:
        player_individual_results = self._player_individual_results()
        player_cumulative_results = self._player_cumulative_results(player_individual_results)

        player_results = self._player_results(
            player_individual_results=player_individual_results,
            player_cumulative_results=player_cumulative_results,
        )
        return results.EventResult(
            players=player_results,
        )

    def _player_individual_results(self) -> dict[str, results.IPlayerEventIndividualResult]:
        return {player_name: player_.individual_result() for player_name, player_ in self._players.items()}

    def _player_cumulative_results(
        self,
        player_individual_results: dict[str, results.IPlayerEventIndividualResult],
    ) -> dict[str, results.PlayerEventCumulativeResult]:
        return CumulativeResults(
            player_individual_results=player_individual_results,
            event_type=self._input.type,
        ).cumulative_results()

    def _player_results(
        self,
        player_individual_results: dict[str, results.IPlayerEventIndividualResult],
        player_cumulative_results: dict[str, results.PlayerEventCumulativeResult],
    ) -> dict[str, results.PlayerEventResult]:
        player_names = player_individual_results.keys()
        if player_names != player_cumulative_results.keys():
            raise EventProcessingError(
                "An error was encountered while processing this event. "
                "Individual and cumulative event results do not have the same set of players."
            )

        return {
            player_name: results.PlayerEventResult(
                individual_result=player_individual_results[player_name],
                cumulative_result=player_cumulative_results[player_name],
            )
            for player_name in player_names
        }


class EventCumulativeResultsGroupingError(Exception):
    """Exception raised when an error is encountered while grouping inidividual player results."""


T = TypeVar("T")


class CumulativeResults:
    def __init__(
        self,
        player_individual_results: dict[str, results.IPlayerEventIndividualResult],
        event_type: inputs.EventType,
    ) -> None:
        self._complete_results = self._group_results_with_class_type(
            player_results=player_individual_results,
            class_type=results.PlayerEventIndividualResult,
        )
        self._incomplete_results = self._group_results_with_class_type(
            player_results=player_individual_results,
            class_type=results.IncompletePlayerEventInividualResult,
        )

        self._verify_grouping_of_results(player_names=list(player_individual_results.keys()))

        self._rank_manager = rank.Rank()
        self._points_manager = points.Points(event_type)

    def _group_results_with_class_type(
        self,
        player_results: dict[str, results.IPlayerEventIndividualResult],
        class_type: type[T],
    ) -> dict[str, T]:
        return {player_name: result for player_name, result in player_results.items() if isinstance(result, class_type)}

    def _verify_grouping_of_results(self, player_names: list[str]) -> None:
        grouped_player_names = set(self._complete_results.keys()).union(set(self._incomplete_results.keys()))

        if grouped_player_names != set(player_names):
            # This should not be reachable, but it's best to prove that theory.
            raise EventCumulativeResultsGroupingError(
                "Player inividual results could not be grouped into complete and " "incomlpete results."
            )

    def cumulative_results(self) -> dict[str, results.PlayerEventCumulativeResult]:
        cumulative_complete_results = self._cumulative_results_from_complete_individual_results()
        highest_event_rank = self._highest_complete_results_rank(cumulative_complete_results)

        cumulative_incomplete_results = self._cumulative_results_from_incomplete_individual_results(
            highest_event_rank_from_complete_results=highest_event_rank,
        )

        return cumulative_complete_results | cumulative_incomplete_results

    def _cumulative_results_from_complete_individual_results(
        self,
    ) -> dict[str, results.PlayerEventCumulativeResult]:
        complete_results = self._complete_results
        player_names = complete_results.keys()

        # TODO: this whole thing feels messy to me
        gross_score_ranks = self._rank_manager.player_ranks_from_values(
            player_values={name: result.total_gross for name, result in self._complete_results.items()},
            rank_order=rank.RankOrder.ASCENDING,
        )
        net_score_ranks = self._rank_manager.player_ranks_from_values(
            player_values={name: result.total_net for name, result in self._complete_results.items()},
            rank_order=rank.RankOrder.ASCENDING,
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
            rank_order=rank.RankOrder.DESCENDING,
        )

        result: dict[str, results.PlayerEventCumulativeResult] = {}
        for name in player_names:
            result[name] = results.PlayerEventCumulativeResult(
                gross_score_points=gross_score_points[name],
                net_score_points=net_score_points[name],
                event_points=event_points[name],
                gross_score_rank=gross_score_ranks[name],
                net_score_rank=net_score_ranks[name],
                event_rank=event_ranks[name],
            )

        return result

    def _highest_complete_results_rank(
        self, cumulative_complete_results: dict[str, results.PlayerEventCumulativeResult]
    ) -> rank.IRankValue:
        is_results_dict_empty = len(cumulative_complete_results) == 0
        if is_results_dict_empty:
            return rank.NoRankValue()

        return max(result.event_rank for result in cumulative_complete_results.values())

    def _cumulative_results_from_incomplete_individual_results(
        self,
        highest_event_rank_from_complete_results: rank.IRankValue,
    ) -> dict[str, results.PlayerEventCumulativeResult]:
        incomplete_results = self._incomplete_results

        event_rank_for_all_incomplete_results = self._event_rank_for_all_incomplete_results(
            highest_event_rank_from_complete_results
        )

        return {
            name: results.PlayerEventCumulativeResult(
                gross_score_points=0.0,
                net_score_points=0.0,
                event_points=0.0,
                gross_score_rank=rank.NoRankValue(),
                net_score_rank=rank.NoRankValue(),
                event_rank=event_rank_for_all_incomplete_results,
            )
            for name in incomplete_results.keys()
        }

    def _event_rank_for_all_incomplete_results(
        self,
        highest_event_rank_from_complete_results: rank.IRankValue,
    ) -> rank.RankValue:
        if isinstance(highest_event_rank_from_complete_results, rank.NoRankValue):
            return rank.RankValue(1)

        else:
            return highest_event_rank_from_complete_results + 1
