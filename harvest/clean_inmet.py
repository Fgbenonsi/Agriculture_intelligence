import polars as pl
from pathlib import Path
from inmet_fetcher.reader import read

df = read(Path("./data"), years=list(range(2000, 2026)))

stations = [
    "COLOMBO", "GOIAS", "JATAI", "MARINGA",
    "RONDONOPOLIS", "SANTA MARIA", "SAO LUIZ GONZAGA"
]

df_filtered = df.filter(pl.col("estacao").is_in(stations))

# Save
out = Path("./weather_7stations.parquet")
df_filtered.write_parquet(out)
print(f"Saved {len(df_filtered)} rows to {out}")
print(df_filtered.group_by("estacao").len().sort("estacao"))