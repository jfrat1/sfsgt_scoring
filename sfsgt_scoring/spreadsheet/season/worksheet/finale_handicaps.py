from typing import NamedTuple

from sfsgt_scoring.spreadsheet import sheet_utils
from sfsgt_scoring.spreadsheet.google import worksheet


class FinaleHandicap(NamedTuple):
    ghin_handicap: float
    season_handicap: float
    finale_handicap: float
    finale_course_handicap: int


class FinaleHandicapsWriteData(dict[str, FinaleHandicap]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


START_COL = "B"
START_ROW = "3"
START_CELL = f"{START_COL}{START_ROW}"
END_COL = "F"


class FinaleHandicapsWorksheet:
    def __init__(
        self,
        worksheet: worksheet.GoogleWorksheet,
        players: list[str],
    ) -> None:
        self._worksheet = worksheet
        self._players = players

    def write(self, write_data: FinaleHandicapsWriteData) -> None:
        num_players = len(self._players)
        end_row = str(int(START_ROW) + num_players - 1)

        end_cell = f"{END_COL}{end_row}"
        write_range = f"{START_CELL}:{end_cell}"

        values: worksheet.CellValues = [
            [
                player,
                player_data.season_handicap,
                player_data.ghin_handicap,
                player_data.finale_handicap,
                player_data.finale_course_handicap,
            ]
            for player, player_data in write_data.items()
        ]

        range_value = worksheet.RangeValues(
            range=write_range,
            values=values,
        )
        self._worksheet.write_range(range_value)
