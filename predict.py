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
        'depends_on_past': False,
        'retries': 0,
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

    # run함수로 모델예측 후 로그 파일 만드는 함수 생성
    def make_logf(**kwargs):
        from datetime import datetime, timedelta
        from threekcal_model.worker import run
        import os
        import csv
        # keyword arguments를 사용하여 분단위로 로그 파일저장
        # log_data 파일 이름 형태는 202410081122
        ts_nodash= kwargs['ts_nodash']
        dt = datetime.strptime(ts_nodash[:-2], '%Y%m%dT%H%M')
        formatted_time = dt.strftime('%Y%m%d%H%M')
        file_path = f'/home/ubuntu/log/{formatted_time}.log'
        dir_path=os.path.dirname(file_path)

        # dir_path가 없으면 dir_path 만들고 save_path 생성
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        save_path = os.path.join(dir_path,f'{formatted_time}.log')
        log_data=run()

        # log_data가 없으면 "없습니다" 출력
        if len(log_data)==0:
            print("log data가 없습니다.")
            return True
        
        # save_path 없으면 생성 후 head 작성
        if not os.path.exists(save_path):
            with open (save_path,mode="w",encoding='utf-8', newline='') as f:
                writer = csv.writer(f) 
                writer.writerow(['num','prediction_result','prediction_score','prediction_time'])
        
        # save_path 있으면 log_data 행 하나씩 읽어서 append
        with open(save_path, mode='a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for i in range(len(log_data)):
                writer.writerow([log_data[i][0], log_data[i][1], log_data[i][2], log_data[i][3]])
       
       # log_data 만들어졌는지 파일크기로 확인
        with open(save_path,mode='r',encoding='utf-8',newline='') as f :
            # csvfile이 비었는지 아닌지 확인
            csvfile = list(csv.reader(f))  
            result = f"저장경로: {save_path}, 파일 크기 : {len(csvfile)}"
        return result

    prediction = PythonVirtualenvOperator(task_id="prediction",
        python_callable=make_logf,
        requirements=["git+https://github.com/ThreeKcal/model.git@0.1.0/me"],
        system_site_packages=False,
        trigger_rule='all_done',
        )
    

    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')

    start >> prediction >> end
