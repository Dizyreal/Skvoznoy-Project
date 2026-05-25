import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

def load_period(period, db_config, table_name):
    mart_path = Path(f"data/mart/mart_{period}.csv")
    
    if not mart_path.exists():
        return 0
    
    df = pd.read_csv(mart_path)
    df['date'] = pd.to_datetime(df['date'])
    
    conn_string = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    engine = create_engine(conn_string)
    
    period_start = f"{period} 00:00:00"
    period_end = f"{period} 23:59:59"
    
    with engine.begin() as conn:
        conn.execute(text(f"DELETE FROM {table_name} WHERE date >= '{period_start}' AND date <= '{period_end}'"))
        df.to_sql(table_name, con=conn, if_exists='append', index=False)
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name} WHERE date >= '{period_start}' AND date <= '{period_end}'"))
        count = result.fetchone()[0]
    
    return count