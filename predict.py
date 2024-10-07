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

    
    def make_logf():
        from threekcal_model.worker import run
        import os
        import csv
        #ds_nodash 2012410071411 
        #print(kwargs['ds_nodash'])
        #print(type(kwargs['ds_nodash']))
        #a=kwargs['ds_nodash'].strfdatetime("%Y-%m-%d %H:%M:%S")
        #print(a)

        file_path = f'/home/ubuntu/log/predict.log'
        #print(file_path)
        dir_path=os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        save_path = os.path.join(dir_path,'predict.log')
        log_data=run()
        
        if not os.path.exists(save_path):
            # 헤더 작성
            with open (save_path,mode="w",encoding='utf-8', newline='') as f:
                writer = csv.writer(f) 
                writer.writerow(['num','prediction_result','prediction_score','prediction_time'])

        num_list = []
        if os.path.exists(save_path):
            with open(save_path, mode='r', encoding='utf-8', newline='') as f:
                csv_reader = csv.reader(f)
                next(csv_reader)  # 헤더 건너뛰기
                num_list = [int(row[0]) for row in csv_reader]  # num 컬럼 값을 리스트로 저장

        # log_data의 항목들을 파일에 추가 (중복되지 않는 경우에만)
        with open(save_path, mode='a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)

            # 파일이 없었다면 헤더 작성
            if not os.path.exists(save_path):
                writer.writerow(['num', 'prediction_result', 'prediction_score', 'prediction_time'])

            # 새로운 데이터를 중복 확인 후 파일에 추가
            new_entries = 0
            for entry in log_data:
                if entry[0] not in num_list:
                    writer.writerow(entry)
                    num_list.append(entry[0])
                    new_entries += 1

            if new_entries == 0:
                print('❌예측할 새로운 데이터가 없습니다.❌')

        # 최종 결과 확인
        with open(save_path, mode='r', encoding='utf-8', newline='') as f:
            csvfile = list(csv.reader(f))
            result = f"저장경로: {save_path}, 파일 크기 : {len(csvfile)} (헤더 포함)"
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
