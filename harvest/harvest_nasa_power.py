import os
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

# Centroids of the main soybean states
STATES = {
    "MT": {"lat": -12.64, "lon": -55.42},  # Mato Grosso
    "PR": {"lat": -24.89, "lon": -51.55},  # Paraná
    "RS": {"lat": -30.03, "lon": -51.22},  # Rio Grande do Sul
    "GO": {"lat": -15.93, "lon": -50.14},  # Goiás
}

PARAMS = "PRECTOTCORR,T2M,T2M_MAX,T2M_MIN,RH2M"
START, END = "20000101", "20251231"
BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

all_frames = []

for uf, coords in STATES.items():
    print(f"Fetching NASA POWER for {uf}...")
    url = (
        f"{BASE_URL}?latitude={coords['lat']}&longitude={coords['lon']}"
        f"&start={START}&end={END}&parameters={PARAMS}"
        f"&community=AG&format=JSON"
    )
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    data = r.json()

    # The API returns a nested dict: parameter -> date -> value
    params_data = data["properties"]["parameter"]
    df = pd.DataFrame(params_data)
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df = df.reset_index().rename(columns={"index": "date"})
    df["uf"] = uf
    all_frames.append(df)

combined = pd.concat(all_frames, ignore_index=True)
print(f"Total rows: {len(combined)}")

# Load into PostgreSQL
with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS weather_nasa"))
    conn.execute(text("""
        CREATE TABLE weather_nasa (
            date DATE NOT NULL,
            uf VARCHAR(2) NOT NULL,
            PRECTOTCORR NUMERIC,
            T2M NUMERIC,
            T2M_MAX NUMERIC,
            T2M_MIN NUMERIC,
            RH2M NUMERIC
        )
    """))

# Use COPY for speed
import io
buffer = io.StringIO()
combined[["date", "uf", "PRECTOTCORR", "T2M", "T2M_MAX", "T2M_MIN", "RH2M"]].to_csv(
    buffer, index=False, header=False
)
buffer.seek(0)

import psycopg
conn_string = os.getenv("DATABASE_URL").replace("postgresql+psycopg://", "postgresql://")
with psycopg.connect(conn_string) as conn:
    with conn.cursor() as cur:
        with cur.copy("""
            COPY weather_nasa (date, uf, PRECTOTCORR, T2M, T2M_MAX, T2M_MIN, RH2M)
            FROM STDIN WITH (FORMAT csv)
        """) as copy:
            copy.write(buffer.read())
    conn.commit()

print("Loaded into weather_nasa.")