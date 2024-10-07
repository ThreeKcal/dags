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


    def get_data():
        from pyspark.main import get_prediction, connection
        data= connection()
        get_prediction=get_prediction()


    save_data = PythonVirtualenvOperator(task_id="save_data",
        python_callable=get_data,
        requirements=["git+ssh://git@github.com:ThreeKcal/pyspark.git0.3", "pyspark==3.5.3"],
        system_site_packages=False,
        trigger_rule='all_done',
        )
    

    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')

    start >> save_data >> end
