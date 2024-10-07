from datetime import datetime, timedelta
import sys
import os
import pandas as pd
from airflow import DAG
import sklearn
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
    'test',
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
    tags=['predict', 'emotion', 'ml'],
    ) as dag:

    
    def make_logf(**kwargs):
        print("hello" * 33)
        #print(f"hello:ds={ds}")
        print(f"hello:kwargs={kwargs}")
        print("hello" * 33)


    prediction = PythonVirtualenvOperator(task_id="prediction",
        python_callable=make_logf,
        requirements=["git+https://github.com/ThreeKcal/model.git@0.1.0/me"],
        system_site_packages=False,
        venv_cache_path='/home/centa/tmp/ven1'
        )
    

    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')

    start >> prediction >> end
