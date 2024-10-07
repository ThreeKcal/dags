from datetime import datetime, timedelta
import sys
import os
import pandas as pd
from airflow import DAG
import subprocess
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import (
        PythonOperator,
        BranchPythonOperator,
        PythonVirtualenvOperator,
)

os.environ['LC_ALL'] = 'C'

with DAG(
    'save_db',
    default_args={
        'depends_on_past': True,
        'retries': 1,
        'retry_delay': timedelta(seconds=3),
    },
    max_active_runs=1,
    max_active_tasks=3,
    description='save_db',
    schedule='*/3 * * * *',
    start_date=datetime(2024, 10, 4),
    end_date=datetime(2024,10,8),
    catchup=False,
    tags=['predict', 'ml', 'db'],
    ) as dag:



    save_data = BashOperator(task_id="savedata",
        bash_command="""
        $SPARK_HOME/bin/spark-submit $AIRFLOW_HOME/py/pyspark_pj3.py "LogToMariaDB"
        """

        )
    

    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')

    start >> save_data >> end
