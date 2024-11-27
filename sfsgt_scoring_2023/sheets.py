# Following along with parts of
# https://www.makeuseof.com/tag/read-write-google-sheets-python/
import functools
import pathlib

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials


class SheetController:
    """Google sheets interaction controller.

    Uses a SFSGT service account. Credentials are stored in a file locally.
    """

    def __init__(self, sheet_name: str) -> None:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            pathlib.Path(__file__).parent.parent / "google_cloud_creds" / "sfsgt-credentials.json",
            scopes=scopes,
        )
        gspread_client = gspread.authorize(credentials)

        self.sheet: gspread.spreadsheet.Spreadsheet = gspread_client.open(sheet_name)

    @functools.lru_cache()
    def worksheet(self, worksheet_name: str) -> gspread.worksheet.Worksheet:
        return self.sheet.worksheet(worksheet_name)

    def worksheet_to_df(self, worksheet_name: str) -> pd.DataFrame:
        ws = self.worksheet(worksheet_name)
        return pd.DataFrame.from_records(ws.get_all_records())

    def worksheet_range_to_df(
        self,
        worksheet_name: str,
        range_name: str,
        has_header_row: bool = False,
    ) -> pd.DataFrame:
        ws = self.worksheet(worksheet_name)
        values = ws.get_values(range_name)

        columns = None
        if has_header_row:
            columns = values[0]
            values = values[1:]

        return pd.DataFrame.from_records(values, columns=columns)

    def write_df_to_worksheet(self, worksheet_name: str, data: pd.DataFrame) -> None:
        """Writes a dataframe to a worksheet by name.

        Column labels are included in the first row for the sheet.

        Index labels are not included. If you want the index to be in the worksheet, it must be
        promoted to a column with df.reset_index() before passing it to this method.
        """
        worksheet = self.worksheet(worksheet_name)

        if data.isnull().values.any():
            raise ValueError(
                "Data cannot have null values. They will be rejected by the google spreadsheet "
                "API. Consider filling null values in data with the `fillna` method of"
                "pd.DataFrame."
            )

        worksheet.update([data.columns.values.tolist()] + data.values.tolist())
