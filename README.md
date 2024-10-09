# model
## Overview
ML 어플리케이션 서비스를 위한 기본 리포지토리

팀 프로젝트 #3: 팀 ThreeKcal

`DistilRoBERTa` 기반의 text classifier 모델인 [michellejieli/emotion_text_classifier](https://huggingface.co/michellejieli/emotion_text_classifier) 을 통해:
- `Streamlit` 기반 웹 어플리케이션을 통해 사용자 입력을 받고, 해당 문장에 대한 sentiment analysis/prediction 실행 (🤬🤢😀😐😭😲)
- 해당 prediction에 대해 실제 sentiment label 및 피드백 코멘트 역시 입력
- Airflow 부분을 더 알고 싶다면 [이 리포지토리](https://github.com/ThreeKcal/dags/tree/main) 확인
- Pyspark 부분을 더 알고 싶다면 [이 리포지토리](https://github.com/ThreeKcal/pyspark/tree/main)  확인


## Features
### `streamlit` [어플리케이션](http://54.180.132.11:8002/) 시연 모습
- `텍스트 업로드` 페이지: 이용자가 `username`과 `comment`를 입력해 데이터베이스로 전송시킵니다
![text_uploadpage](https://github.com/user-attachments/assets/1099ff86-8491-4002-b375-5f0dbe3e8bfc)

- `코멘트 라벨` 페이지: 전체 혹은 `username` 기준으로 추려낸 코멘트에 관리자가 실제 `label` 값 및 추가 사항을 입력할 수 있습니다
![commentlabelpage](https://github.com/user-attachments/assets/b2c8be3b-54a2-4366-bcf9-5943f40c5569)

- `결과 통계` 페이지: 위 두 페이지를 통해 형성된 데이터베이스에 대한 각종 통계 자료를 볼 수 있습니다. 새로고침할 때마다 새롭게 변경사항을 반영합니다.
![statistic_dynamic](https://github.com/user-attachments/assets/a4f7656e-9a57-46e8-a85b-e6be9c187305)


### Structure
![Blank_diagram_-_Page_1_2](https://github.com/user-attachments/assets/2c2cfbd5-fa7e-4cee-858b-57ccb84e6715)

본 에어플로우 어플리케이션은 `predict.py`, `pyspark_db.py`, `pyspark_pj3.py`로 이루어져 있습니다.

- `prediction.py` : 실제 모델 적용 및 예측을 실행하는 DAG 입니다. 해당 예측 프로세스에 대한 로그파일 역시 본 DAG에서 실행합니다.
![image](https://github.com/user-attachments/assets/dce759a2-cf03-4b02-89e5-e44340c9c44e)

- `pyspark_db.py` : `prediction.py` 의 로그파일이 생성된 후 이를 받아 시간변수를 추가해 `pyspark_pj3.py`로 전송합니다.

- `pyspark_pj3.py` : 전송된 값 및 변수를 기반으로 `pyspark`과 연동, `mariadb` 데이터베이스를 업데이트합니다.
 
### 생성된 에어플로우 로그 파일 디렉토리 및 실제 내부 값
![image](https://github.com/user-attachments/assets/c733df6d-e212-4565-8dfb-28b1963bc901)

![image](https://github.com/user-attachments/assets/982106c8-cfbc-42dc-aadb-9c74c00ac2a9)


### Usage
- `fastapi` 서버 런칭
```bash
$ uvicorn src/threekcal_model/api:app --host 0.0.0.0 --port 8000
```

- `steamlit` 서버 런칭
```bash
$ streamlit run src/threekcal_model/streamlit/main.py --server.port 9000
```

## 개발 관련 사항
### 타임라인
![스크린샷 2024-10-10 010952](https://github.com/user-attachments/assets/7bed00cb-272e-49e1-83f4-3986dd6bfcff)

※ 권한이 있는 이용자는 [프로젝트 schedule](https://github.com/orgs/ThreeKcal/projects/1/views/4)에서 확인할 수 있습니다.

### `troubleshooting`
- 본 리포지토리 및 연관 리포지토리들의 `issues`, `pull request` 쪽을 참조해 주세요.
