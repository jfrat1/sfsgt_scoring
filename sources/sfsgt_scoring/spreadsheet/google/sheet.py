import functools
import pathlib
from typing import Any

import gspread

from sfsgt_scoring.spreadsheet.google import worksheet

SERVICE_ACCOUNT_CREDENTIALS_FILE = (
    pathlib.Path(__file__).parent.parent.parent.parent.parent / "google_cloud_creds" / "sfsgt-credentials.json"
)


class GoogleSheet:
    """Google sheets interaction controller.

    Uses a SFSGT service account. Credentials are stored in a file locally.
    """

    def __init__(self, sheet_id: str) -> None:
        gspread_client = gspread.service_account(filename=SERVICE_ACCOUNT_CREDENTIALS_FILE)

        self.sheet: gspread.spreadsheet.Spreadsheet = gspread_client.open_by_key(sheet_id)

    @functools.lru_cache()
    def worksheet(self, worksheet_name: str) -> worksheet.GoogleWorksheet:
        return worksheet.GoogleWorksheet(worksheet=self.sheet.worksheet(worksheet_name))

    @functools.lru_cache()
    def sheet_metadata(self) -> Any:
        return self.sheet.fetch_sheet_metadata()

    def worksheet_titles(self) -> list[str]:
        sheets_metadata = self.sheet_metadata()["sheets"]
        return [sheet_meta["properties"]["title"] for sheet_meta in sheets_metadata]
