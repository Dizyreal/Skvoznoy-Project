import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator

with DAG(
    dag_id="demo_fixed",
    start_date=pendulum.datetime(2026, 3, 1, tz="UTC"),
    schedule="*/5 * * * *",
    catchup=False,
):
    EmptyOperator(task_id="dummy")