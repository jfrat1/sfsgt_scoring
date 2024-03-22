import functools
import pathlib
from typing import Any

from oauth2client import service_account
import gspread

from sfsgt_scoring.spreadsheet.google import worksheet

CREDENTIALS_FILE = pathlib.Path(__file__).parent.parent.parent.parent / "google_cloud_creds" / "sfsgt-credentials.json"


class GoogleSheet():
    """Google sheets interaction controller.

    Uses a SFSGT service account. Credentials are stored in a file locally.
    """

    def __init__(self, sheet_id: str) -> None:
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = service_account.ServiceAccountCredentials.from_json_keyfile_name(
            filename=CREDENTIALS_FILE,
            scopes=scopes
        )
        gspread_client = gspread.authorize(credentials)

        self.sheet: gspread.spreadsheet.Spreadsheet = gspread_client.open_by_key(sheet_id)

    @functools.lru_cache()
    def worksheet(self, worksheet_name: str) -> worksheet.GoogleWorksheet:
        return worksheet.GoogleWorksheet(worksheet=self.sheet.worksheet(worksheet_name))

    @functools.lru_cache()
    def sheet_metadata(self) -> Any:
        return self.sheet.fetch_sheet_metadata()

    def worksheet_titles(self) -> set[str]:
        sheets_metadata = self.sheet_metadata()["sheets"]
        return {sheet_meta["properties"]["title"] for sheet_meta in sheets_metadata}
