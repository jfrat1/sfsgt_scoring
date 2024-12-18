import abc
from typing import Any, Mapping

import gspread

from google_sheet import worksheet


class GoogleSheetController(abc.ABC):
    @abc.abstractmethod
    def worksheet(self, worksheet_name: str) -> worksheet.GoogleWorksheet:
        pass

    @abc.abstractmethod
    def sheet_metadata(self) -> Mapping[str, Any]:
        pass

    @abc.abstractmethod
    def worksheet_titles(self) -> list[str]:
        pass


class ConcreteGoogleSheetController(GoogleSheetController):
    def __init__(self, gspread_client: gspread.client.Client, sheet_id: str) -> None:
        self._sheet: gspread.spreadsheet.Spreadsheet = gspread_client.open_by_key(sheet_id)

    def worksheet(self, worksheet_name: str) -> worksheet.GoogleWorksheet:
        return worksheet.GoogleWorksheet(worksheet=self._sheet.worksheet(worksheet_name))

    def sheet_metadata(self) -> Mapping[str, Any]:
        return self._sheet.fetch_sheet_metadata()

    def worksheet_titles(self) -> list[str]:
        worksheets_metadata = self.sheet_metadata()["sheets"]
        return [sheet_meta["properties"]["title"] for sheet_meta in worksheets_metadata]
