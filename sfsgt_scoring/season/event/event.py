
from . import course, inputs, player, results


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
        return {
            player_name: player_.individual_result()
            for player_name, player_ in self._players.items()
        }

    def _player_cumulative_results(
        self,
        player_individual_results: dict[str, results.IPlayerEventIndividualResult],
    ) -> dict[str, results.CumulativePlayerEventResult]:
        # Split results into complete / incomplete
        # Process complete results:
        #   calc net and gross rank
        #   calc net, gross, and total points
        # Incomplete scores get 0 points
        # Calc event rank for all players, including incomplete scores

        complete_results = {
            player_name: result
            for player_name, result in player_individual_results.items()
            if isinstance(result, results.PlayerEventIndividualResult)
        }

        incomplete_results = {
            player_name: result
            for player_name, result in player_individual_results.items()
            if isinstance(result, results.IncompletePlayerEventInividualResult)
        }

        assert len(complete_results) + len(incomplete_results) == len(player_individual_results)




        # TODO: unimplemented
        return None

    def _player_results(
        self,
        player_individual_results: dict[str, results.IPlayerEventIndividualResult],
        player_cumulative_results: dict[str, results.CumulativePlayerEventResult],
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
