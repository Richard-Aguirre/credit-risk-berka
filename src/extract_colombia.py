"""
Extract the Colombian loan portfolio data from the datos.gov.co API and load it into Neon.
"""

import pandas as pd
import requests
from src.load import get_engine, load_to_raw

URL = "https://www.datos.gov.co/resource/rvii-eis8.json"


def fetch_all_rows():
    """
    We create a loop to get the data from the API in batches of 1,000 rows and then we add them to a list called all_rows. Returns a DataFrame with all the rows.
    """
    page_size = 1000
    offset = 0
    all_rows = []
    while True:
        params = {"$limit": page_size, "$offset": offset, "$order": ":id"}
        response = requests.get(URL, params=params)
        page = response.json()
        if len(page) == 0:
            break
        all_rows.extend(page)
        offset += page_size
    return pd.DataFrame(all_rows)


def get_last_date(engine):
    """
    Return the last cutoff date of the Colombian loan portfolio in the Neon database, as text. 
    """
    return pd.read_sql("SELECT MAX(fecha_corte) FROM raw.co_loan_portfolio", engine).iloc[0, 0]