import pandas as pd
from gspread import utils as gspread_utils

a1_to_rowcol = gspread_utils.a1_to_rowcol
rowcol_to_a1 = gspread_utils.rowcol_to_a1


def is_cell_a1_notation(cell_name: str) -> bool:
    """Returns true if a string matches a cell's A1 notation.

    Ex:
      - "A1" -> True
      - "B" -> False
      - "1" -> False
    """
    # Use fullmatch to ensure that we match on the entire string.
    match = gspread_utils.CELL_ADDR_RE.fullmatch(string=cell_name)
    is_a1_notation = match is not None
    return is_a1_notation


def is_range_a1_notation(range_name: str) -> bool:
    """Returns true if a string matches a ranges's A1 notation.

    Ex:
      - "A1:G9" -> True
      - "B:D5" -> False
      - "A7:G" -> False
    """
    # Use fullmatch to ensure that we match on the entire string.
    match = gspread_utils.A1_ADDR_FULL_RE.fullmatch(string=range_name)
    is_a1_notation = match is not None
    return is_a1_notation


def column_idx_to_letter(col_idx: int) -> str:
    dummy_row_idx = 1
    cell_name = gspread_utils.rowcol_to_a1(row=dummy_row_idx, col=col_idx)

    column_str = cell_name.replace(str(dummy_row_idx), "")
    return column_str


def column_letter_to_idx(col_letter: str) -> int:
    return gspread_utils.column_letter_to_index(col_letter)


def numericise_all_values(data: pd.DataFrame) -> pd.DataFrame:
    return data.map(gspread_utils.numericise)


def replace_empty_strings_with_none(data: pd.DataFrame) -> pd.DataFrame:
    data_out = data.copy()
    data_out[data_out == ""] = None
    return data_out
