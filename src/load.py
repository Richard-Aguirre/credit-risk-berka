"""
Load Berka dataset to Neon using DATABASE_URL environment variable.
The data is loaded into the raw schema of the Neon database.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
from src.extract import load_table

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


TABLES = {
    "loan": None,
    "account": None, 
    "card": None, 
    "client": None, 
    "disp": None, 
    "district": None, 
    "order": None,
    "trans": {"bank": str}
}


def get_engine():
    """
    Create a connection to the Neon database and return a SQLAlchemy engine.
    """
    load_dotenv(ENV_PATH)  # Load the .env variables into the environment.
    db_url = os.getenv("DATABASE_URL")  # Read the connection URL from the environment.
    if db_url is None:  # Stop with a clear error if DATABASE_URL is missing.
        raise ValueError("DATABASE_URL is not set")
    engine = create_engine(db_url, pool_pre_ping=True)
    return engine


def load_to_raw(df, table_name, engine, if_exists="replace"):
    """
    Load a DataFrame into the raw schema of the Neon database.
    if_exists: "replace" (default) drops and recreates the table;
    "append" adds the rows to the existing table.
    """
    df.to_sql(table_name, engine, schema="raw", if_exists=if_exists, index=False, chunksize=10000)
    print(f"{table_name} loaded")


def verify_rows(df, table_name, engine):
    """
    Compare the row count of the DataFrame with the table in Neon and raise an error if they don't match
    """
    db_rows = pd.read_sql(f'SELECT COUNT(*) FROM raw."{table_name}"', engine).iloc[0, 0]
    csv_rows = df.shape[0]
    print(f"{table_name}, csv_rows={csv_rows}, db_rows={db_rows}, ok={csv_rows == db_rows}")
    if db_rows != csv_rows:
        raise ValueError(f"{table_name}: db_rows:{db_rows} and csv_rows:{csv_rows} didn't match")


def main():
    """
    Load each Berka table into the raw schema and verify its row count.
    """
    engine = get_engine()
    for table_name, dtype in TABLES.items():
        df = load_table(table_name, dtype)
        load_to_raw(df, table_name, engine)
        verify_rows(df, table_name, engine)


if __name__ == "__main__":
    main()