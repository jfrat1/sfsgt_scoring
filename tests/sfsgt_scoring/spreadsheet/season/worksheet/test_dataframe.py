import pandas as pd
from pandas import testing as pd_testing
from sfsgt_scoring.spreadsheet.season.worksheet import dataframe


def test_numericise_all_values_nominal() -> None:
    input_df = pd.DataFrame(
        data=[
            ["23", "34", "56"],
            ["1.6", "14.8", "22.7"],
        ]
    )

    numericised_df = dataframe.numericise_all_values(input_df)
    pd_testing.assert_frame_equal(left=numericised_df, right=pd.DataFrame(data=[[23, 34, 56], [1.6, 14.8, 22.7]]))


def test_numericise_all_values_doesnt_modify_non_numeric_strings() -> None:
    input_df = pd.DataFrame(
        data=[
            ["23", "34", "foo"],
            ["1.6", "bar", "22.7"],
        ]
    )

    numericised_df = dataframe.numericise_all_values(input_df)
    pd_testing.assert_frame_equal(left=numericised_df, right=pd.DataFrame(data=[[23, 34, "foo"], [1.6, "bar", 22.7]]))


def test_numericise_all_values_doesnt_modify_empty_strings() -> None:
    input_df = pd.DataFrame(
        data=[
            ["23", "34", ""],
            ["1.6", "", "22.7"],
        ]
    )

    numericised_df = dataframe.numericise_all_values(input_df)
    pd_testing.assert_frame_equal(left=numericised_df, right=pd.DataFrame(data=[[23, 34, ""], [1.6, "", 22.7]]))


def test_numericise_all_values_doesnt_modify_numeric_values() -> None:
    input_df = pd.DataFrame(
        data=[
            ["23", "34", 56],
            ["1.6", 14.8, "22.7"],
        ]
    )

    numericised_df = dataframe.numericise_all_values(input_df)
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

    modified_df = dataframe.replace_empty_strings_with_none(input_df)
    expected_df = pd.DataFrame(
        data=[
            ["23", "34", None],
            ["1.6", "14.8", "22.7"],
        ]
    )
    pd_testing.assert_frame_equal(left=modified_df, right=expected_df)


def test_replace_empty_string_with_none_integer_values() -> None:
    input_df = pd.DataFrame(data=[[2, 4, 6], [3, "", 9]])

    modified_df = dataframe.replace_empty_strings_with_none(input_df)

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
