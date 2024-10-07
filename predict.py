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
    tags=['predict', 'emotion', 'ml'],
    ) as dag:

    
    def make_logf(**kwargs):
        from threekcal_model.worker import run
        import os
        import csv
        #ds_nodash 2012410071411 
        print(kwargs['ds_nodash'])
        print(type(kwargs['ds_nodash']))
        a=kwargs['ds_nodash'].strfdatetime("%Y-%m-%d %H:%M:%S")
        print(a)

        file_path = f'/home/ubuntu/log/predict.log'
        print(file_path)
        dir_path=os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        save_path = os.path.join(dir_path,'predict.log')
        log_data=run()
        
        if not os.path.exists(save_path):
            with open (save_path,mode="w",encoding='utf-8', newline='') as f:
                writer = csv.writer(f) 
                writer.writerow(['num','prediction_result','prediction_score','prediction_time'])

        with open(save_path, mode='a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for i in range(len(log_data)):
                writer.writerow([log_data[i][0], log_data[i][1], log_data[i][2], log_data[i][3]])
       
        with open(save_path,mode='r',encoding='utf-8',newline='') as f :
            # csvfile이 비었는지 아닌지 확인
            csvfile = list(csv.reader(f))  
            result = f"저장경로: {save_path}, 파일 크기 : {len(csvfile)}"
        return result

    prediction = PythonVirtualenvOperator(task_id="prediction",
        python_callable=make_logf,
        requirements=["git+https://github.com/ThreeKcal/model.git@0.1.0/me"],
        system_site_packages=True,
        trigger_rule='all_done',
        )
    

    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')

    start >> prediction >> end
