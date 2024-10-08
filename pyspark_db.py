from datetime import datetime, timedelta
import sys
import os
import pandas as pd
from airflow import DAG
import subprocess
from airflow.models import Variable
from airflow.sensors.external_task import ExternalTaskSensor
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
        'depends_on_past': False,
        'retries': 1,
        'retry_delay': timedelta(seconds=3),
    },
    max_active_runs=1,
    max_active_tasks=3,
    description='save_db',
    schedule='*/3 * * * *',
    start_date=datetime(2024, 10, 4),
    end_date=datetime(2024,10,8),
    catchup=True,
    tags=['predict', 'ml', 'db'],
    ) as dag:
    

    # Model Dag의 predict task를 실행할 때 까지 대기 시키는 센서오퍼레이터
    wait_logf = ExternalTaskSensor(
    task_id='wait_logf',
    external_dag_id='predict_emotion',  # DAG A의 ID
    external_task_id='prediction',  # DAG A의 마지막 태스크 ID (필요한 경우)
    allowed_states=['success'],
    failed_states=['failed', 'skipped'],
    timeout=300,  # 5분 내에 완료되지 않으면 타임아웃
    )

    save_data = BashOperator(
        task_id="savedata",
        bash_command="""
        $SPARK_HOME/bin/spark-submit /home/centa/code/3kcal/dags/pyspark_pj3.py {{data_interval_start.strftime('%Y%m%d%H%M')}}
        """
        )

    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')

    start >> wait_logf >> save_data >> end
