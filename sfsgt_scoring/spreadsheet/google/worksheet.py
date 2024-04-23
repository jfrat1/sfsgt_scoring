from typing import Iterable, NamedTuple

import gspread
import pandas as pd

CellValueType = str | float | int


class RangeValues(NamedTuple):
    range: str
    # Represents a 2-d array of data values to be written into the range. The
    # inner lists are rows to be written.
    values: list[list[CellValueType]]


class GoogleWorksheet:
    def __init__(self, worksheet: gspread.worksheet.Worksheet) -> None:
        self.worksheet = worksheet

    def to_df(self) -> pd.DataFrame:
        return pd.DataFrame.from_records(self.worksheet.get_all_records())

    def range_to_df(
        self,
        range: str,
        has_header_row: bool = False,
    ) -> pd.DataFrame:
        values: list[list[str]] = self.worksheet.get_values(range_name=range, maintain_size=True)

        columns = None
        if has_header_row:
            columns = values[0]
            values = values[1:]

        return pd.DataFrame.from_records(values, columns=columns)

    def write_df(self, data: pd.DataFrame) -> None:
        """Writes a dataframe to a worksheet by name.

        Column labels are included in the first row for the sheet.

        Index labels are not included. If you want the index to be in the worksheet, it must be
        promoted to a column with df.reset_index() before passing it to this method.
        """
        if data.isnull().values.any():
            raise ValueError(
                "Data cannot have null values. They will be rejected by the google spreadsheet API. "
                "Consider filling null values in data with the `fillna` method of pd.DataFrame."
            )

        self.worksheet.update(
            [data.columns.values.tolist()] + data.values.tolist()
        )

    def write_multiple_ranges(self, range_values: Iterable[RangeValues]) -> None:
        write_data = [
            {"range": range_value.range, "values": range_value.values}
            for range_value in range_values
        ]
        self.worksheet.batch_update(data=write_data)
