from datetime import datetime, timedelta
import sys
import os
import pandas as pd
from airflow import DAG
import sklearn
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import (
        PythonOperator,
        BranchPythonOperator,
        PythonVirtualenvOperator,

)
with DAG(
    'predict_emotion',
    default_args={
        'depends_on_past': True,
        'retries': 1,
        'retry_delay': timedelta(seconds=3),
    },
    max_active_runs=1,
    max_active_tasks=3,
    description='predict_emotion',
    schedule='*/3 * * * *',
    start_date=datetime(2024, 10, 4),
    end_date=datetime(2024,10,8),
    catchup=True,
    tags=['predict', 'emotion'],
) as dag:

    def import_run():
        from threekcal_model.worker import run 
        return run()

    prediction = PythonVirtualenvOperator(task_id="prediction",
            python_callable=import_run,
            requirements=["git+https://github.com/ThreeKcal/model.git@0.1.0/model"],
            system_site_packages=True,
            trigger_rule='all_done'
            )

    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')

    start >> prediction >> end
