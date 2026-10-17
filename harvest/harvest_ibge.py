"""
Harvest soybean production data from IBGE/SIDRA.

Table 1612: Produção Agrícola Municipal
Classification c81/2713: Soybean (Soja em grão)
Variables: 109 (area planted), 214 (production), 216 (area harvested)
"""

import os
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://fabriceg@localhost:5433/agri_intel")
engine = create_engine(DATABASE_URL)

# --- Configuration ---
TABLE = "1612"
CLASSIFICATION = "c81/2713"  # Soybean
VARIABLES = "109,214,216"    # Area planted, Production, Area harvested
PERIOD = "all"
TERRITORY = "n1/all"         # Brazil national level

BASE_URL = "https://apisidra.ibge.gov.br/values"

VARIABLE_MAP = {
    "109": "area_planted_ha",
    "214": "production_t",
    "216": "area_harvested_ha",
}


def fetch_ibge():
    url = f"{BASE_URL}/t/{TABLE}/{TERRITORY}/p/{PERIOD}/v/{VARIABLES}/{CLASSIFICATION}"
    print(f"Fetching: {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    # First element is the header, rest are data rows
    header = data[0]
    rows = data[1:]

    # Convert to DataFrame
    df = pd.DataFrame(rows)

    # Keep only the columns we need
    df = df[["D1N", "D2N", "D3C", "D4C", "V", "MN"]]
    df = df.rename(columns={
        "D1N": "state_name",
        "D2N": "year",
        "D3C": "variable_code",
        "D4C": "crop_code",
        "V": "value",
        "MN": "unit",
    })

    # Map variable codes to column names
    df["variable"] = df["variable_code"].map(VARIABLE_MAP)

    # Pivot variables into columns
    df_pivot = df.pivot_table(
        index=["state_name", "year", "crop_code"],
        columns="variable",
        values="value",
        aggfunc="first",
    ).reset_index()

    # Clean types
    df_pivot["year"] = pd.to_numeric(df_pivot["year"], errors="coerce").astype("Int64")
    for col in ["area_planted_ha", "production_t", "area_harvested_ha"]:
        if col in df_pivot.columns:
            df_pivot[col] = pd.to_numeric(df_pivot[col], errors="coerce")

    # Add metadata
    df_pivot["country"] = "BRA"
    df_pivot["crop"] = "soybean"
    df_pivot["source"] = "IBGE/SIDRA"
    df_pivot["state_code"] = None
    df_pivot["state_name"] = df_pivot["state_name"].replace({"Brasil": "Brazil"})

    # Select final columns in schema order
    final_cols = [
        "country", "state_code", "state_name", "municipality_code",
        "municipality_name", "year", "crop", "production_t",
        "area_planted_ha", "area_harvested_ha", "yield_kg_ha", "source",
    ]
    for col in final_cols:
        if col not in df_pivot.columns:
            df_pivot[col] = None

    df_pivot = df_pivot[final_cols]

    # Compute yield
    df_pivot["yield_kg_ha"] = (
        df_pivot["production_t"] * 1000 / df_pivot["area_harvested_ha"]
    ).round(2)

    return df_pivot


def load_to_db(df):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM production WHERE country = 'BRA' AND crop = 'soybean'"))

    df.to_sql("production", engine, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into production")


if __name__ == "__main__":
    df = fetch_ibge()
    print(df.head())
    print(f"Total rows: {len(df)}")
    load_to_db(df)
    print("Done.")