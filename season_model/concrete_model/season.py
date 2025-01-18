from season_model.api.input import SeasonModelInput
from season_model.api.model import SeasonModel
from season_model.api.result import SeasonModelResults


class ConcreteSeasonModel(SeasonModel):
    def calculate_results(self, input: SeasonModelInput) -> SeasonModelResults:
        pass
