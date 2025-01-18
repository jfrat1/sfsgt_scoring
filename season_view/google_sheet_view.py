from typing import NamedTuple

import google_sheet
from season_view.api import read_data, view, write_data


class GoogleSheetSeasonViewConfig(NamedTuple):
    pass


class GoogleSheetSeasonView(view.SeasonView):
    def __init__(
        self,
        config: GoogleSheetSeasonViewConfig,
        sheet_controller: google_sheet.GoogleSheetController,
    ) -> None:
        self._config = config
        self._sheet_controller = sheet_controller

    def read_season(self) -> read_data.SeasonViewReadData:
        pass

    def write_season(self, data: write_data.SeasonViewWriteData) -> None:
        pass
