"""
Harvest soybean trade data from Comex Stat CSV files.

Downloads yearly CSV files directly from the government database.
Filters for NCM codes starting with 1201 (soybeans).
"""

import os
import io
import urllib3
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://fabriceg@localhost:5433/agri_intel")
engine = create_engine(DATABASE_URL)

SOYBEAN_NCM_PREFIX = "1201"
BASE_URL = "https://balanca.mdic.gov.br/balanca/bd/comexstat-bd/ncm"


def fetch_year(year):
    """Download one year of export data and filter for soybeans."""
    url = f"{BASE_URL}/EXP_{year}.csv"
    print(f"Downloading {url}...")

    try:
        response = requests.get(url, timeout=120, verify=False)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to download {year}: {e}")
        return pd.DataFrame()

    df = pd.read_csv(io.StringIO(response.text), sep=";", encoding="utf-8")

    # Filter for soybean NCMs (codes starting with 1201)
    df = df[df["CO_NCM"].astype(str).str.startswith(SOYBEAN_NCM_PREFIX)]

    if df.empty:
        print(f"  No soybean records for {year}")
        return pd.DataFrame()

    df = df.rename(columns={
        "CO_ANO": "year",
        "CO_MES": "month",
        "KG_LIQUIDO": "volume_kg",
        "VL_FOB": "value_usd",
        "CO_NCM": "ncm_code",
    })

    df = df[["year", "month", "ncm_code", "volume_kg", "value_usd"]]

    df["country"] = "BRA"
    df["flow"] = "export"
    df["ncm_description"] = "Soybeans"
    df["crop"] = "soybean"
    df["source"] = "Comex Stat CSV"
    df["state_code"] = None
    df["partner_country"] = None

    print(f"  {len(df)} rows for {year}")
    return df


def fetch_comex(start_year=2015, end_year=2025):
    """Download multiple years."""
    all_data = []

    for year in range(start_year, end_year + 1):
        df = fetch_year(year)
        if not df.empty:
            all_data.append(df)

    if not all_data:
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)


def load_to_db(df):
    if df.empty:
        print("No data to load.")
        return
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM trade WHERE country = 'BRA' AND crop = 'soybean'"))
    df.to_sql("trade", engine, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into trade")


if __name__ == "__main__":
    df = fetch_comex(start_year=2015, end_year=2025)
    if not df.empty:
        print(f"\nTotal rows: {len(df)}")
        print(df.head())
        load_to_db(df)
        print("Done.")
    else:
        print("No data downloaded.")