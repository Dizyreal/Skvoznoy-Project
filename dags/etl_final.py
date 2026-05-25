import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

default_args = {
    "owner": "student",
    "retries": 1,
}

with DAG(
    dag_id="etl_final",
    default_args=default_args,
    start_date=pendulum.datetime(2026, 5, 1, tz="UTC"),
    schedule="*/10 * * * *",
    catchup=False,
) as dag:

    start = EmptyOperator(task_id="start")

    extract = BashOperator(
        task_id="extract",
        bash_command="""
        cd /opt/airflow && \
        python -c "
import sys
sys.path.insert(0, '/opt/airflow')
from src.week6.extract import extract
raw_path = extract('configs/variant_15.yml', 'data/raw/variant_15')
print(f'raw saved: {raw_path}')
"
        """,
    )

    transform = BashOperator(
        task_id="transform",
        bash_command="""
        cd /opt/airflow && \
        python -c "
import sys
sys.path.insert(0, '/opt/airflow')
from src.week6.transform import transform
import glob
period = '{{ ds }}'
raw_files = glob.glob('data/raw/variant_15/*.json')
if raw_files:
    mart_path, max_date = transform(raw_files[-1], 'data/mart', 'reference/regions.csv', period=period)
    print(f'mart saved: {mart_path}')
    import pandas as pd
    df = pd.read_csv(mart_path)
    print(f'mart rows: {len(df)}')
"
        """,
    )

    dq = BashOperator(
        task_id="dq",
        bash_command="""
        cd /opt/airflow && \
        python -c "
import sys
sys.path.insert(0, '/opt/airflow')
from src.week8.dq import run_dq_period
period = '{{ ds }}'
result = run_dq_period(period)
if not result:
    sys.exit(1)
print('DQ passed')
"
        """,
    )

    load = BashOperator(
        task_id="load",
        bash_command="""
        cd /opt/airflow && \
        python -c "
import sys
sys.path.insert(0, '/opt/airflow')
from src.week6.load import load
import pandas as pd
from pathlib import Path
period = '{{ ds }}'
mart_path = f'data/mart/mart_{period}.csv'
if not Path(mart_path).exists():
    mart_files = list(Path('data/mart').glob('*.csv'))
    if mart_files:
        mart_path = str(mart_files[0])
    else:
        print('No mart files found')
        sys.exit(1)
DB_CONFIG = {'user': 'airflow', 'password': 'airflow', 'host': 'postgres', 'port': '5432', 'database': 'analytics'}
row_count = load(mart_path, DB_CONFIG, 'mart_earthquakes', mode='replace')
print(f'loaded rows to postgres: {row_count}')
"
        """,
    )

    end = EmptyOperator(task_id="end")

    start >> extract >> transform >> dq >> load >> end