from __future__ import annotations

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup

REPO_DIR = "/opt/airflow/repo"
DBT_DIR = f"{REPO_DIR}/dbt/commerce_data_platform"
DBT_PROFILES_DIR = f"{REPO_DIR}/dbt"  # contains profiles.yml

# Runs your ingestion module from repo root (so imports work)
INGEST_CMD = "python -m src.ingestion.run_ingest"

default_args = {
    "owner": "commerce-data-platform",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="commerce_data_platform_daily",
    default_args=default_args,
    description="Ingest DummyJSON -> BigQuery raw -> dbt staging/marts",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    tags=["bigquery", "dbt", "ingestion"],
) as dag:

    batch_date = "{{ ds }}"  # Airflow run date: YYYY-MM-DD

    with TaskGroup(group_id="ingestion") as ingestion:
        ingest_users = BashOperator(
            task_id="ingest_users",
            bash_command=f"cd {REPO_DIR} && {INGEST_CMD} --entity users --batch_date {batch_date}",
        )

        ingest_products = BashOperator(
            task_id="ingest_products",
            bash_command=f"cd {REPO_DIR} && {INGEST_CMD} --entity products --batch_date {batch_date}",
        )

        ingest_carts = BashOperator(
            task_id="ingest_carts",
            bash_command=f"cd {REPO_DIR} && {INGEST_CMD} --entity carts --batch_date {batch_date}",
        )

        # users + products can run in parallel, then carts
        [ingest_users, ingest_products] >> ingest_carts

    dbt_run_staging = BashOperator(
        task_id="dbt_run_staging",
        bash_command=(
            f"cd {DBT_DIR} && "
            f"dbt run --profiles-dir {DBT_PROFILES_DIR} --select staging"
        ),
    )

    dbt_run_marts = BashOperator(
        task_id="dbt_run_marts",
        bash_command=(
            f"cd {DBT_DIR} && "
            f"dbt run --profiles-dir {DBT_PROFILES_DIR} --select marts"
        ),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            f"cd {DBT_DIR} && "
            f"dbt test --profiles-dir {DBT_PROFILES_DIR} --select staging marts"
        ),
    )

    ingestion >> dbt_run_staging >> dbt_run_marts >> dbt_test
