"""
Extract the Colombian loan portfolio data from the datos.gov.co API and load it into Neon.
"""

import pandas as pd
import requests
from sqlalchemy import text
from src.load import get_engine, load_to_raw, verify_rows

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


def fetch_new_rows(last_date):
    """
    Return a DataFrame with the API rows after the last date recorded in Neon.
    """
    params = {"$where": f"fecha_corte>'{last_date}'", "$limit": 50000}
    response = requests.get(URL, params=params)
    return pd.DataFrame(response.json())


def get_source_updated_at():
    """
    Return the date of the last update of the API dataset, as text. 
    """
    params = {"$select": "max(:updated_at)"}
    data = requests.get(URL, params=params).json()
    return data[0]["max_updated_at"]


def get_last_loaded_source(engine):
    """
    Return the last source update date that was loaded successfully, or None if nothing has been loaded yet.
    """
    return pd.read_sql("SELECT MAX(source_updated_at) FROM raw.co_load_log WHERE status = 'success'", engine).iloc[0, 0]


def is_new_publication(source_updated_at, last_loaded):
    """
    Compare the API update date with the last successful load. Return True if there is a new publication to 
    load (or nothing has been loaded yet); otherwise, return False.
    """
    if pd.isna(last_loaded):
        return True
    source_date = pd.to_datetime(source_updated_at, utc=True)
    return source_date != last_loaded


def record_load(engine, source_updated_at, rows_loaded, status):
    """
    Insert a new record in raw.co_load_log with the source update date, the number of rows loaded and the load status.
    """
    with engine.begin() as conn:
        conn.execute(text("""INSERT INTO raw.co_load_log (source_updated_at, rows_loaded, status) 
                             VALUES(:source_updated_at, :rows_loaded, :status)"""), 
                             {"source_updated_at": source_updated_at, "rows_loaded": rows_loaded, "status": status})


def reconcile_counts(engine):
    """
    Compare the number of rows per cutoff date in Neon and in the API. If the numbers don't match, raise an error; otherwise,
    print "Monthly counts match."
    """
    neon_counts = pd.read_sql("SELECT fecha_corte, COUNT(*) AS neon_rows FROM raw.co_loan_portfolio GROUP BY fecha_corte", engine)
    params = {"$select": "fecha_corte, count(*) as api_rows", "$group": "fecha_corte", "$limit": 50000}
    api_counts = pd.DataFrame(requests.get(URL, params=params).json())
    api_counts["api_rows"] = api_counts["api_rows"].astype(int)
    merge = neon_counts.merge(api_counts, on = "fecha_corte", how = "outer").sort_values(by="fecha_corte")
    mismatches = merge[merge["neon_rows"] != merge["api_rows"]]
    if not mismatches.empty:
        raise ValueError(f"Monthly counts don't match:\n{mismatches}")
    print("Monthly counts match")


def main():
    """
    Check if the API has a new publication. If it does, reload the whole table, verify the rows and add a record in 
    raw.co_load_log; otherwise, print "No new data". If something goes wrong, register "failed" in the log and raise the error.
    """
    engine = get_engine()
    api_date = get_source_updated_at()
    log_date = get_last_loaded_source(engine)
    if not is_new_publication(api_date, log_date):
        print("No new data")
        return
    try:
        df = fetch_all_rows()
        load_to_raw(df, "co_loan_portfolio", engine)
        verify_rows(df, "co_loan_portfolio", engine)
        reconcile_counts(engine)
        record_load(engine, api_date, df.shape[0], "success")
    except Exception:
        record_load(engine, api_date, 0, "failed")
        raise


if __name__ == "__main__":
    main()