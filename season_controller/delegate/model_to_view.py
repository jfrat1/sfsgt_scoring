from typing import NamedTuple

import season_model
import season_view


class SeasonModelToViewDelegate(NamedTuple):
    model_results: season_model.SeasonModelResults

    def generate_view_write_data(self) -> season_view.SeasonViewWriteData:
        pass
