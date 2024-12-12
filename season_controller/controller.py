from typing import NamedTuple

import season_config
import season_model
import season_view
from season_controller.translators import (
    SeasonViewToModelTranslator,
    SeasonModelToViewTranslator,
)


class SeasonController:
    def __init__(
        self,
        model: season_model.SeasonModel,
        view: season_view.SeasonView,
        config: season_config.SeasonConfig,
    ) -> None:
        self.model = model
        self.view = view
        self.config = config


    def run_season(self) -> None:
        view_read_data = self.view.read()

        model_input = SeasonViewToModelTranslator(
            view_read_data
        ).translate()

        model_results = self.model.calculate_results(model_input)

        view_write_data = SeasonModelToViewTranslator(
            model_results
        ).translate()

        self.view.write(view_write_data)
