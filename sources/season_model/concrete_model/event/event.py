from season_model.api.input import SeasonModelEventInput
from season_model.api.result import (
    SeasonModelEventPlayerAggregateResult,
    SeasonModelEventPlayerIndividualResult,
    SeasonModelEventPlayerResult,
    SeasonModelEventResult,
)
from season_model.concrete_model.event.aggregate import EventAggregateResultsGenerator
from season_model.concrete_model.event.individual import PlayerIndividualResultGenerator


class EventResultGenerator:
    def __init__(
        self,
        input: SeasonModelEventInput,
    ) -> None:
        self._input = input

    def generate(self) -> SeasonModelEventResult:
        individual_results = self._individual_results()
        aggregate_results = self._aggregate_results(individual_results=individual_results)

        player_results: list[SeasonModelEventPlayerResult] = []
        for player in self._input.player_names:
            player_results.append(
                SeasonModelEventPlayerResult(
                    name=player,
                    individual_result=individual_results[player],
                    aggregate_result=aggregate_results[player],
                )
            )

        return SeasonModelEventResult(
            name=self._input.event_name,
            players=player_results,
        )

    def _individual_results(self) -> dict[str, SeasonModelEventPlayerIndividualResult]:
        individual_results: dict[str, SeasonModelEventPlayerIndividualResult] = {}
        for player in self._input.player_names:
            player_input = self._input.player(player)
            player_tee = self._input.tee_for_player(gender=player_input.gender)

            individual_results[player] = PlayerIndividualResultGenerator(
                input=player_input,
                course=self._input.course,
                tee=player_tee,
            ).generate()

        return individual_results

    def _aggregate_results(
        self,
        individual_results: dict[str, SeasonModelEventPlayerIndividualResult],
    ) -> dict[str, SeasonModelEventPlayerAggregateResult]:
        return EventAggregateResultsGenerator(
            individual_results=individual_results,
            event_type=self._input.event_type,
        ).generate()
