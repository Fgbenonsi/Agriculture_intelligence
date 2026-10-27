import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# Local (source)
local = create_engine("postgresql+psycopg://fabriceg@localhost:5433/agri_intel")

# Aiven (target)
aiven_url = os.getenv("AIVEN_DATABASE_URL")
aiven = create_engine(aiven_url)

for table in ["soybean_forecasts", "soybean_feature_importance"]:
    print(f"Pushing {table}...")
    df = pd.read_sql(f"SELECT * FROM {table}", local)
    df.to_sql(table, aiven, if_exists="replace", index=False)
    print(f"  {len(df)} rows pushed to Aiven")