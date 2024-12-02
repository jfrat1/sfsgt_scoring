from typing import NamedTuple

from season_view.view_api import read_data, view, write_data


class GoogleSheetSeasonViewConfig(NamedTuple):
    pass


class GoogleSheetSeasonView(view.SeasonView):
    def __init__(self, config: GoogleSheetSeasonViewConfig) -> None:
        self._config = config

    def read(self) -> read_data.SeasonViewReadData:
        pass

    def write(self, data: write_data.SeasonViewWriteData) -> None:
        pass
