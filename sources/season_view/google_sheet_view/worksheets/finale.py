import re

import google_sheet
from google_sheet import utils as sheet_utils
from google_sheet.worksheet import CellValues

from season_view.api import write_data


class FinaleWorksheetError(Exception):
    pass


class FinaleWorksheet:
    def __init__(
        self,
        worksheet_controller: google_sheet.GoogleWorksheet,
        player_names_range: str,
        season_handicap_column: str,
        finale_handicap_index_column: str,
        course_handicap_column: str,
    ) -> None:
        self._worksheet_controller = worksheet_controller

        self.player_names_range = player_names_range
        self.season_handicap_column = season_handicap_column
        self.finale_handicap_index_column = finale_handicap_index_column
        self.course_handicap_column = course_handicap_column

    def _verify_configuration(self) -> None:
        if not sheet_utils.is_range_a1_notation(self.player_names_range):
            raise FinaleWorksheetError(f"Player names range must be in A1:B2 notation: {self.player_names_range}")

        ## TODO: Add more checks that configured columns are columns labels

    def write(self, data: write_data.SeasonViewWriteFinaleData) -> None:
        # Before writing, read the players that are in the handicaps section
        # Since range_to_df returns a dataframe, we have to use `[0]` to turn it into a series
        players = self._worksheet_controller.range_to_df(range=self.player_names_range)[0].to_list()

        season_handicaps: list[float] = []
        finale_handicap_indices: list[float] = []
        finale_course_handicaps: list[int | None] = []

        for player in players:
            player_data = data.get_player(player)
            season_handicaps.append(player_data.season_handicap_index)
            finale_handicap_indices.append(player_data.finale_handicap_index)
            finale_course_handicaps.append(player_data.finale_course_handicap)

        write_ranges: list[google_sheet.RangeValues] = []

        season_handicap_range = replace_column_letter_unknown_old(self.player_names_range, self.season_handicap_column)
        write_ranges.append(
            google_sheet.RangeValues(range=season_handicap_range, values=list_to_column_range_value(season_handicaps))
        )

        finale_indexes_range = replace_column_letter_unknown_old(
            self.player_names_range, self.finale_handicap_index_column
        )
        write_ranges.append(
            google_sheet.RangeValues(
                range=finale_indexes_range, values=list_to_column_range_value(finale_handicap_indices)
            )
        )

        finale_course_handicaps_range = replace_column_letter_unknown_old(
            self.player_names_range, self.course_handicap_column
        )
        write_ranges.append(
            google_sheet.RangeValues(
                range=finale_course_handicaps_range, values=list_to_column_range_value(finale_course_handicaps)
            )
        )

        self._worksheet_controller.write_multiple_ranges(write_ranges)


def replace_column_letter_unknown_old(a1_notation: str, new_column_letter: str):
    # """
    # Replaces the column letter(s) in a spreadsheet A1 notation string,
    # without needing to know the original letters.
    #
    # Args:
    #     a1_notation: The original A1 notation string (e.g., "A1:C26" or "X5").
    #     new_column_letter: The new column letter(s) (e.g., "N").
    #
    # Returns:
    #     The modified A1 notation string (e.g., "N1:N26" or "N5").
    # """
    # The pattern r"^[A-Z]+" matches one or more uppercase letters at the start
    # of the string (e.g., "A" in "A1", or "AA" in "AA1").
    modified_notation = re.sub(r"^[A-Z]+", new_column_letter, a1_notation)

    # The pattern r":[A-Z]+" matches a colon followed by one or more uppercase
    # letters (for the end of a range, if present).
    # This ensures both column letters in a range are updated.
    modified_notation = re.sub(r":[A-Z]+", ":" + new_column_letter, modified_notation)

    return modified_notation


def list_to_column_range_value(list: list[google_sheet.CellValueType]) -> CellValues:
    output: CellValues = []
    for value in list:
        output.append([value])

    return output
