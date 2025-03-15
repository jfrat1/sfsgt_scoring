import pandas as pd
from gspread import utils


def numericise_all_values(data: pd.DataFrame) -> pd.DataFrame:
    return data.map(utils.numericise)


def replace_empty_strings_with_none(data: pd.DataFrame) -> pd.DataFrame:
    data_out = data.copy()
    data_out[data_out == ""] = None
    return data_out
