import enum
from typing import Any, Iterable, Literal, NamedTuple, Optional, Self

import gspread
import gspread_formatting
import pandas as pd
from gspread import utils as gspread_utils

from google_sheet import utils as sheet_utils

CellValueType = str | float | int
CellValues = list[list[CellValueType]]


class RangeValues(NamedTuple):
    range: str
    # Represents a 2-d array of data values to be written into the range. The
    # inner lists are rows to be written.
    values: CellValues


class RgbValueOutOfRangeError(Exception):
    """Exception to be raised when an RGB value is out of range."""


class ColorRgb:
    """Color as reg, green, blue values. Values must be integers in the interval [0, 255]."""

    min_rgb_int = 0
    max_rgb_int = 255

    def __init__(self, red: int, green: int, blue: int) -> None:
        self._verify_rgb_value("red", red)
        self._verify_rgb_value("green", green)
        self._verify_rgb_value("blue", blue)

        self.red = red
        self.green = green
        self.blue = blue

    def as_google_api_dict(self) -> dict[str, float]:
        return {
            "red": self._rgb_int_to_float(self.red),
            "green": self._rgb_int_to_float(self.green),
            "blue": self._rgb_int_to_float(self.blue),
        }

    @classmethod
    def from_color(cls, color: gspread_formatting.Color) -> Self:
        """Create a ColorRgb from a Color object. Convert float RGB values to integer RGB values."""
        return cls(
            red=round(color.red * cls.max_rgb_int),
            green=round(color.green * cls.max_rgb_int),
            blue=round(color.blue * cls.max_rgb_int),
        )

    def _is_in_rgb_range(self, rgb_val: int) -> bool:
        return rgb_val >= self.min_rgb_int and rgb_val <= self.max_rgb_int

    def _verify_rgb_value(self, rgb_name: str, rgb_val: int) -> None:
        if not self._is_in_rgb_range(rgb_val):
            raise RgbValueOutOfRangeError(
                f"RGB values must be in the interval [0, 1]. Got {rgb_val} for color {rgb_name}."
            )

    def _rgb_int_to_float(self, rgb_int: int) -> float:
        return rgb_int / self.max_rgb_int

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ColorRgb):
            return NotImplemented

        return self.red == other.red and self.green == other.green and self.blue == other.blue


class CellFormat(NamedTuple):
    background_color: Optional[ColorRgb] = None

    def as_google_api_dict(self) -> dict[str, dict[str, dict[str, float]]]:
        api_json = {}
        if self.background_color is not None:
            api_json["backgroundColorStyle"] = {"rgbColor": self.background_color.as_google_api_dict()}

        return api_json


class RangeFormat(NamedTuple):
    # Range in A-1 range notation
    range: str
    format: CellFormat

    def as_google_api_cell_format(self) -> gspread.worksheet.CellFormat:
        return gspread.worksheet.CellFormat(range=self.range, format=self.format.as_google_api_dict())


class SortOrder(enum.Enum):
    ASCENDING = enum.auto()
    DESCENDING = enum.auto()

    def gspread_sort_order(self) -> Literal["asc", "des"]:
        match self:
            case SortOrder.ASCENDING:
                return "asc"
            case SortOrder.DESCENDING:
                return "des"
            case _:
                # This should not be reachable unless a new enum variant is added without
                # adding it to this match statement.
                raise ValueError(f"Unknown {self.__class__.__name__} enum variant.")


class SortSpec(NamedTuple):
    column: str
    order: SortOrder

    def column_idx(self) -> int:
        return gspread_utils.column_letter_to_index(self.column)


class GoogleWorksheet:
    def __init__(self, worksheet: gspread.worksheet.Worksheet) -> None:
        self.worksheet = worksheet

    def to_df(
        self,
        header_row: int = 1,
        expected_headers: Any | None = None,
    ) -> pd.DataFrame:
        return pd.DataFrame.from_records(
            self.worksheet.get_all_records(head=header_row, expected_headers=expected_headers)
        )

    def range_values(
        self,
        range: str,
    ) -> list[list[str]]:
        return self.worksheet.get_values(range_name=range, maintain_size=True)

    def column_range_values(self, column: str, first_row: int, last_row: int) -> list[str]:
        range = f"{column}{first_row}:{column}{last_row}"
        range_values = self.range_values(range=range)

        # range_values is a list of lists where the inner lists hold
        # row values with a length of 1. Flatten the inner lists to
        # produce a 1-D array.
        return [row[0] for row in range_values]

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
                "Data cannot have null values. They will be rejected by the google spreadsheet"
                "API. Consider filling null values in data with the `fillna` method "
                "of pd.DataFrame."
            )

        self.worksheet.update([data.columns.values.tolist()] + data.values.tolist())

    def write_range(self, range_value: RangeValues) -> None:
        self.worksheet.update(
            values=range_value.values,
            range_name=range_value.range,
        )

    def write_multiple_ranges(self, range_values: Iterable[RangeValues]) -> None:
        write_data = [{"range": range_value.range, "values": range_value.values} for range_value in range_values]
        self.worksheet.batch_update(data=write_data)

    def sort_range(self, specs: Iterable[SortSpec], range_name: str) -> None:
        if not sheet_utils.is_range_a1_notation(range_name):
            raise ValueError(
                "The 'range' argument must be a valid A1 range name, e.g. 'A1:C6'.\n" f"Found: {range_name}."
            )

        gspread_specs = [(spec.column_idx(), spec.order.gspread_sort_order()) for spec in specs]

        self.worksheet.sort(*gspread_specs, range=range_name)

    def format_multiple_ranges(self, range_formats: Iterable[RangeFormat]) -> None:
        formats = [format.as_google_api_cell_format() for format in range_formats]
        self.worksheet.batch_format(formats=formats)

    def cell_format(self, cell: str) -> CellFormat:
        if not sheet_utils.is_cell_a1_notation(cell):
            raise ValueError(f"Cell must be in A1 notation: {cell}.")

        format_raw = gspread_formatting.get_effective_format(worksheet=self.worksheet, label=cell)
        return CellFormat(background_color=ColorRgb.from_color(format_raw.backgroundColor))
