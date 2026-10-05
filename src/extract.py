import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def load_table(table_name, dtype=None):
    """
    Load a raw Berka CSV from data/raw/

    Args:
        table_name: table name
        dtype: type of data in a column (int,str etc),
            EX : {column, type of data}, {"bank" : str}

    Returns: The table as a pandas DataFrame
    """
    path = RAW_DIR/ f"{table_name}.csv"
    return pd.read_csv(path, sep=";",dtype=dtype)