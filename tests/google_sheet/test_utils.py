from google_sheet import utils as sheet_utils


def test_is_cell_a1_notation_true() -> None:
    assert sheet_utils.is_cell_a1_notation("A1")
    assert sheet_utils.is_cell_a1_notation("B6")
    assert sheet_utils.is_cell_a1_notation("ZZ300")


def test_is_cell_a1_notation_false() -> None:
    assert not sheet_utils.is_cell_a1_notation("A")
    assert not sheet_utils.is_cell_a1_notation("6")
    assert not sheet_utils.is_cell_a1_notation("A1A")


def test_is_range_a1_notation_true() -> None:
    assert sheet_utils.is_range_a1_notation("A1:B6")
    assert sheet_utils.is_range_a1_notation("A9:Z27")
    assert sheet_utils.is_range_a1_notation("AA12:GG22")


def test_is_range_a1_notation_false() -> None:
    assert not sheet_utils.is_range_a1_notation("A:B6")
    assert not sheet_utils.is_range_a1_notation("A9:Z")
    assert not sheet_utils.is_range_a1_notation("AA12A:GG22")


def test_column_idx_to_letter() -> None:
    assert sheet_utils.column_idx_to_letter(1) == "A"
    assert sheet_utils.column_idx_to_letter(2) == "B"
    assert sheet_utils.column_idx_to_letter(26) == "Z"
    assert sheet_utils.column_idx_to_letter(52) == "AZ"
    assert sheet_utils.column_idx_to_letter(2000) == "BXX"


def test_column_letter_to_idx() -> None:
    assert sheet_utils.column_letter_to_idx("A") == 1
    assert sheet_utils.column_letter_to_idx("B") == 2
    assert sheet_utils.column_letter_to_idx("Z") == 26
    assert sheet_utils.column_letter_to_idx("AZ") == 52
    assert sheet_utils.column_letter_to_idx("BXX") == 2000
