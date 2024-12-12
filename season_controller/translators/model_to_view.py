from typing import NamedTuple

import season_model
import season_view

class SeasonModelToViewTranslator(NamedTuple):
    model_results: season_model.SeasonModelResults

    def translate(self) -> season_view.SeasonViewWriteData:
        pass