import os
import io
import pandas as pd
import psycopg
from dotenv import load_dotenv

load_dotenv()
conn_string = os.getenv("DATABASE_URL").replace("postgresql+psycopg://", "postgresql://")

CSV = "/Users/fabriceg/Downloads/Arquivos Finais/yield_forecasting_data_preprocessed.csv"

df = pd.read_csv(CSV)
df = df.drop(columns=["Unnamed: 0"], errors="ignore")

print(f"Loaded {len(df)} rows")
print(df.columns.tolist())

with psycopg.connect(conn_string) as conn:
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS soybean_ml")
        cur.execute("""
            CREATE TABLE soybean_ml (
                harvested INT,
                code VARCHAR(20),
                state VARCHAR(50),
                county VARCHAR(100),
                climate_zone VARCHAR(10),
                yield NUMERIC,
                yield_trend NUMERIC,
                yield_trend_corrected NUMERIC,
                month INT,
                mean_srad NUMERIC,
                mean_tmin NUMERIC,
                mean_tmax NUMERIC,
                hot_days INT,
                acc_rainfall NUMERIC,
                lowrain_days INT,
                oni NUMERIC,
                soy_area NUMERIC,
                mean_ndvi NUMERIC,
                mean_evi NUMERIC,
                mean_cvi NUMERIC,
                mean_gli NUMERIC,
                spi1 NUMERIC,
                spi3 NUMERIC,
                sti1 NUMERIC,
                year INT,
                exc NUMERIC,
                etp NUMERIC,
                def NUMERIC,
                previous_yield NUMERIC
            )
        """)
    conn.commit()
    print("Table created.")

buffer = io.StringIO()
df.to_csv(buffer, index=False, header=False)
buffer.seek(0)

with psycopg.connect(conn_string) as conn:
    with conn.cursor() as cur:
        with cur.copy("""
            COPY soybean_ml FROM STDIN WITH (FORMAT csv)
        """) as copy:
            copy.write(buffer.read())
    conn.commit()

print(f"Loaded {len(df)} rows into soybean_ml")