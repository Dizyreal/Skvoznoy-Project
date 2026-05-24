# src/week6/load.py
import pandas as pd
from sqlalchemy import create_engine, text

def load(mart_path, db_config, table_name, mode='replace'):
    df = pd.read_csv(mart_path)
    df['date'] = pd.to_datetime(df['date'])
    
    conn_string = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    engine = create_engine(conn_string)
    
    with engine.begin() as conn:
        if mode == 'replace':
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
            df.to_sql(table_name, con=conn, if_exists='replace', index=False)
        elif mode == 'append':
            existing = pd.read_sql(f"SELECT DISTINCT date FROM {table_name}", con=conn)
            if not existing.empty:
                existing['date'] = pd.to_datetime(existing['date'])
                new_df = df[~df['date'].isin(existing['date'])]
            else:
                new_df = df
            if len(new_df) > 0:
                new_df.to_sql(table_name, con=conn, if_exists='append', index=False)
    
    with engine.begin() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.fetchone()[0]
    
    return count