
from sfsgt_scoring.spreadsheet.google import worksheet

class EventWorksheet:
    def __init__(self, worksheet: worksheet.GoogleWorksheet) -> None:
        self.worksheet = worksheet

    def verify(self) -> None:
        pass