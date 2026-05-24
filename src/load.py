import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
from datetime import datetime

MART_PATH = Path("data/mart/mart_daily_2026-05-24_*.csv")
MART_PATH = list(Path("data/mart").glob("mart_daily_*.csv"))[0]

DB_USER = "analyst"
DB_PASSWORD = "mysecretpassword"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "earthquakes_db"

TABLE_NAME = "mart_earthquakes_california"

df = pd.read_csv(MART_PATH)
df['date'] = pd.to_datetime(df['date'])

connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)

with engine.begin() as conn:
    conn.execute(text(f"DROP TABLE IF EXISTS {TABLE_NAME}"))
    print(f"Dropped table {TABLE_NAME}")

with engine.begin() as conn:
    df.to_sql(TABLE_NAME, con=conn, if_exists='replace', index=False)
    print(f"Loaded {len(df)} rows into {TABLE_NAME}")

with engine.begin() as conn:
    result = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}"))
    count = result.fetchone()[0]
    print(f"Verification: {count} rows in {TABLE_NAME}")

print("Load completed successfully")