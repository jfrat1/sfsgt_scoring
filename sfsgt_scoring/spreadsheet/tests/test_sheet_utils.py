from .. import sheet_utils


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


def test_column_letter_for_idx() -> None:
    assert sheet_utils.column_letter_for_idx(1) == "A"
    assert sheet_utils.column_letter_for_idx(2) == "B"
    assert sheet_utils.column_letter_for_idx(26) == "Z"
    assert sheet_utils.column_letter_for_idx(52) == "AZ"
    assert sheet_utils.column_letter_for_idx(2000) == "BXX"
