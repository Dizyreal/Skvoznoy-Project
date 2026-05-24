import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

DB_CONFIG = {
    "user": "student",
    "password": "student_pw",
    "host": "localhost",
    "port": "5432",
    "database": "analytics"
}
TABLE_NAME = "mart_earthquakes"

mart_files = list(Path("data/mart").glob("*.csv"))
if not mart_files:
    raise FileNotFoundError("No mart files found")

df = pd.read_csv(mart_files[0])
df['date'] = pd.to_datetime(df['date'])

conn_string = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(conn_string)

with engine.begin() as conn:
    conn.execute(text(f"DROP TABLE IF EXISTS {TABLE_NAME}"))
    df.to_sql(TABLE_NAME, con=conn, if_exists='replace', index=False)
    result = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}"))
    print(f"Loaded {result.fetchone()[0]} rows into {TABLE_NAME}")