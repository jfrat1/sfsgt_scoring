import pandas as pd
from pandas import testing as pd_testing

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


def test_numericise_all_values_nominal() -> None:
    input_df = pd.DataFrame(
        data=[
            ["23", "34", "56"],
            ["1.6", "14.8", "22.7"],
        ]
    )

    numericised_df = sheet_utils.numericise_all_values(input_df)
    pd_testing.assert_frame_equal(left=numericised_df, right=pd.DataFrame(data=[[23, 34, 56], [1.6, 14.8, 22.7]]))


def test_numericise_all_values_doesnt_modify_non_numeric_strings() -> None:
    input_df = pd.DataFrame(
        data=[
            ["23", "34", "foo"],
            ["1.6", "bar", "22.7"],
        ]
    )

    numericised_df = sheet_utils.numericise_all_values(input_df)
    pd_testing.assert_frame_equal(left=numericised_df, right=pd.DataFrame(data=[[23, 34, "foo"], [1.6, "bar", 22.7]]))


def test_numericise_all_values_doesnt_modify_empty_strings() -> None:
    input_df = pd.DataFrame(
        data=[
            ["23", "34", ""],
            ["1.6", "", "22.7"],
        ]
    )

    numericised_df = sheet_utils.numericise_all_values(input_df)
    pd_testing.assert_frame_equal(left=numericised_df, right=pd.DataFrame(data=[[23, 34, ""], [1.6, "", 22.7]]))


def test_numericise_all_values_doesnt_modify_numeric_values() -> None:
    input_df = pd.DataFrame(
        data=[
            ["23", "34", 56],
            ["1.6", 14.8, "22.7"],
        ]
    )

    numericised_df = sheet_utils.numericise_all_values(input_df)
    pd_testing.assert_frame_equal(
        left=numericised_df,
        right=pd.DataFrame(
            data=[
                [23, 34, 56],
                [1.6, 14.8, 22.7],
            ]
        ),
    )


def test_replace_empty_string_with_none() -> None:
    input_df = pd.DataFrame(
        data=[
            ["23", "34", ""],
            ["1.6", "14.8", "22.7"],
        ]
    )

    modified_df = sheet_utils.replace_empty_strings_with_none(input_df)
    expected_df = pd.DataFrame(
        data=[
            ["23", "34", None],
            ["1.6", "14.8", "22.7"],
        ]
    )
    pd_testing.assert_frame_equal(left=modified_df, right=expected_df)


def test_replace_empty_string_with_none_integer_values() -> None:
    input_df = pd.DataFrame(data=[[2, 4, 6], [3, "", 9]])

    modified_df = sheet_utils.replace_empty_strings_with_none(input_df)

    expected_df = (
        pd.DataFrame(
            data=[
                [2, 4, 6],
                [3, None, 9],
            ]
        )
        .astype(
            dtype={1: object},  # Cast 2nd column to object dtype to match modified_df
        )
        .replace(float("nan"), None)
    )  # Convert NaN to None to match the function under test

    pd_testing.assert_frame_equal(left=modified_df, right=expected_df)
