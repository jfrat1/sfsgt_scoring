import abc

from season_model.model_api import input, result


class SeasonModel(abc.ABC):
    @abc.abstractmethod
    def calculate_results(self, input: input.SeasonModelInput) -> result.SeasonModelResults:
        pass
