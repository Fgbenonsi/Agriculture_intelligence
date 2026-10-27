import os
import io
import polars as pl
import psycopg
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
conn_string = os.getenv("DATABASE_URL").replace("postgresql+psycopg://", "postgresql://")

df = pl.read_parquet(Path("./weather_7stations.parquet"))

cols = [
    "data_hora", "estacao", "codigo_wmo", "uf",
    "precipitacao", "temperatura_maxima", "temperatura_minima",
    "temperatura_ar", "umidade_relativa", "vento_velocidade",
]
df = df.select(cols)

# Convert to pandas for the CSV buffer
df_pd = df.to_pandas()

with psycopg.connect(conn_string) as conn:
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS weather")
        cur.execute("""
            CREATE TABLE weather (
                id SERIAL PRIMARY KEY,
                data_hora TIMESTAMP NOT NULL,
                estacao VARCHAR(100) NOT NULL,
                codigo_wmo VARCHAR(20),
                uf VARCHAR(2),
                precipitacao NUMERIC,
                temperatura_maxima NUMERIC,
                temperatura_minima NUMERIC,
                temperatura_ar NUMERIC,
                umidade_relativa NUMERIC,
                vento_velocidade NUMERIC
            )
        """)
    conn.commit()
    print("Table created.")

buffer = io.StringIO()
df_pd.to_csv(buffer, index=False, header=False)
buffer.seek(0)

with psycopg.connect(conn_string) as conn:
    with conn.cursor() as cur:
        with cur.copy("""
            COPY weather (
                data_hora, estacao, codigo_wmo, uf,
                precipitacao, temperatura_maxima, temperatura_minima,
                temperatura_ar, umidade_relativa, vento_velocidade
            ) FROM STDIN WITH (FORMAT csv)
        """) as copy:
            copy.write(buffer.read())
    conn.commit()

print(f"Loaded {len(df_pd)} rows into weather")