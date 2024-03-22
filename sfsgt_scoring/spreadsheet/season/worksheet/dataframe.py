import pandas as pd
from gspread import utils


def numericise_all_values(data: pd.DataFrame) -> pd.DataFrame:
    return data.map(utils.numericise)
