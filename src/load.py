"""
Load Berka dataset to Neon using DATABASE_URL environment variable.
The data is loaded into the raw schema of the Neon database.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine


ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


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


def load_to_raw(df, table_name, engine):
    df.to_sql(table_name, engine, schema="raw", if_exists="replace", index=False, chunksize=10000)
    print(f"{table_name} loaded")