from season_model.model_api.input import SeasonModelInput
from season_model.model_api.model import SeasonModel
from season_model.model_api.result import SeasonModelResults


class ConcreteSeasonModel(SeasonModel):
    def calculate_results(self, input: SeasonModelInput) -> SeasonModelResults:
        pass
