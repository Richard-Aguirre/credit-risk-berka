# Credit Risk Berka

> 🚧 **Work in progress.** This project is still being built. The data pipeline is already running; the cleaning, analysis and dashboard are next. MVP target: **December 8, 2026**.

## Why this project

Banks lose money when a customer stops paying a loan. Usually, by the time the loan is officially "in default", it's too late to do much about it. But a customer's bank account often tells the story earlier: income stops coming in, the balance keeps dropping, spending changes.

This project tries to answer one question:

> **Which patterns in a customer's account activity signal that they won't pay back their loan, and which customer segments concentrate the most risk?**

The goal is to build a dashboard that a credit risk analyst or manager could use to spot warning signs *before* a loan goes bad.

## The data

**1. Berka dataset (main data)**
Real, anonymized data from a Czech bank (1993–1998), published for the PKDD'99 challenge. It has 8 related tables: loans, accounts, clients, transactions, cards, orders, dispositions and districts.

- 682 loans, of which **76 (11%) went bad**: 31 finished unpaid and 45 still running with the client in debt.
- More than **1 million transactions**, which is where the behavior patterns are hidden.

**2. Colombian loan portfolio (context)**
Open data from Colombia's financial regulator (Superintendencia Financiera), pulled from the [datos.gov.co API](https://www.datos.gov.co/resource/rvii-eis8.json). It shows how much of each bank's loan portfolio is past due, by product and by month. This answers a second question: *what does credit delinquency look like in Colombia today, how has it changed since 2015, and in which credit types and institutions is it concentrated?*

## How it works

```
CSV files (Berka) ─┐
                   ├──► Python / pandas ──► PostgreSQL (Neon) ──► Streamlit dashboard
datos.gov.co API ──┘         ▲                 raw → processed        (coming soon)
                             │
                  GitHub Actions (runs daily)
```

| Tool | What it's used for |
|---|---|
| Python + pandas | Extracting, cleaning and transforming the data |
| PostgreSQL on Neon | Cloud database, with a `raw` schema (data as received) and a `processed` schema (clean data) |
| SQLAlchemy | Connecting Python to the database |
| GitHub Actions | Updating the Colombian data automatically every day |
| Streamlit | The dashboard (in progress) |

## What's done so far

- ✅ Explored all 8 Berka tables and documented their meaning (the original values are in Czech).
- ✅ Loaded all Berka tables into the database, checking that the row counts match the source files.
- ✅ Built an automated pipeline for the Colombian data that:
  - downloads the data from the API in pages of 1,000 rows,
  - **only reloads when a new month is published**, instead of downloading everything every day,
  - checks that the number of rows per month matches the API,
  - keeps a log of every load (successful or failed) in the database.
- ✅ Cleaned the Colombian data in a notebook: grouped 32 loan groups into 4 credit types (consumer, commercial, housing, microcredit) and calculated the past-due balance and delinquency rate.

## What's next

- [ ] Move the Colombian cleaning step from the notebook into `src/` so it runs automatically.
- [ ] Clean the Berka tables and build customer-level features from transactions (income stability, balance trends, etc.).
- [ ] Analyze which patterns and segments are linked to default.
- [ ] Build and publish the Streamlit dashboard.

## Project structure

```
credit-risk-berka/
├── .github/workflows/   # Daily automated load (GitHub Actions)
├── data/                # Raw Berka CSV files (not uploaded to GitHub)
├── notebooks/           # Step-by-step exploration, documented in English
│   ├── 01_first_look.ipynb
│   ├── 02_load_practice.ipynb
│   ├── 03_neon_connection.ipynb
│   ├── 04_colombia_api.ipynb
│   └── 05_colombia_cleaning.ipynb
└── src/                 # Pipeline code
    ├── extract.py             # Reads the Berka CSV files
    ├── load.py                # Connects to Neon and loads the data
    ├── extract_colombia.py    # Downloads and loads the Colombian data
    └── transform_colombia.py  # Cleaning rules for the Colombian data
```

## Run it yourself

1. Clone the repo and install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Download the Berka dataset and put the CSV files in `data/raw/`.
3. Create a `.env` file with your PostgreSQL connection string:
   ```
   DATABASE_URL=postgresql+psycopg://user:password@host/dbname
   ```
4. Load the data:
   ```bash
   python -m src.load              # Berka tables
   python -m src.extract_colombia  # Colombian loan portfolio
   ```

## About me

I'm Richard Aguirre, and I'm building this project to grow as a **Data Analyst** and **Data Engineer**. It covers both sides of the work: building a reliable, automated data pipeline, and turning that data into answers a business can act on. Feedback is very welcome, so feel free to open an issue.
