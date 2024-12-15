from typing import NamedTuple

from season_view.view_api import read_data, view, write_data


class GoogleSheetSeasonViewConfig(NamedTuple):
    pass


class GoogleSheetSeasonView(view.SeasonView):
    def __init__(self, config: GoogleSheetSeasonViewConfig) -> None:
        self._config = config

    def read_season(self) -> read_data.SeasonViewReadData:
        pass

    def write_season(self, data: write_data.SeasonViewWriteData) -> None:
        pass
