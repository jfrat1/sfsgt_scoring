import abc

from season_model.model_api import input, result


class SeasonModel(abc.ABC):
    @abc.abstractmethod
    def run_season(self, input: input.SeasonModelInput) -> result.SeasonModelResult:
        pass
