import gspread
import pandas as pd

class GoogleWorksheet:
    def __init__(self, worksheet: gspread.worksheet.Worksheet) -> None:
        self.worksheet = worksheet

    def to_df(self) -> pd.DataFrame:
        return pd.DataFrame.from_records(self.worksheet.get_all_records())

    def range_to_df(
        self,
        range_name: str,
        has_header_row: bool = False,
    ) -> pd.DataFrame:
        values = self.worksheet.get_values(range_name)

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
