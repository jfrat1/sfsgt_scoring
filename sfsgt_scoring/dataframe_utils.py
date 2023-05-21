from typing import Any

import pandas as pd

def fill_na_dtype_safe(df: pd.DataFrame | pd.Series, fill_value: Any) -> pd.DataFrame | pd.Series:
    """Fill NA values in a dataframe in a way that is safe to column dtypes.

    When filling a column of a particular datatype with a value that is of another
    type, a warning is raised by pandas (v2.1), which will become an error in the future.
    This function changes the datatype of columns that will be filled to an
    "object" dtype, which is generic and allows mixed data.
    """
    for col in df:
        if df[col].isna().any():
            df[col] = df[col].astype('object')
            df[col].fillna(value=fill_value, inplace=True)

    return df
