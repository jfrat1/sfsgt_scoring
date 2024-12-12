from typing import NamedTuple

import season_model
import season_view


class SeasonViewToModelTranslator(NamedTuple):
    view_read_data: season_view.SeasonViewReadData

    def translate(self) -> season_model.SeasonModelInput:
        pass
