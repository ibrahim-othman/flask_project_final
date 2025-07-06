from datetime import datetime, timedelta
import json
import pandas as pd
import csv

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'Esayed',
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    "start_date": days_ago(1),
}

dag = DAG(
    'monitor_the_api_history_per_day',
    default_args=default_args,
    description='A simple DAG to save data to a CSV file',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

# Example task to save data to CSV

# -------variables---------------------------------------------
api_file_path = "./files/API_file.json"
api_history_file_path = "./files/API_History.csv"

# ------------functions-----------------------------------------
def read_api_history(file_path=api_history_file_path):
    Api_History = pd.read_csv(file_path)
    Api_History['date'] = pd.to_datetime(Api_History['date'])
    Api_History['used'] = Api_History['used'].astype(int)
    print("API history is readed")
    return Api_History

def read_api_from_more_than_month(Api_History):
    extract = Api_History['date'] < datetime.now() - timedelta(days=31)
    Api_from_more_than_month = Api_History[extract]
    print("read_api_from_more_than_month are readed")
    return Api_from_more_than_month

def read_api_from_less_than_or_equal_month(Api_History):
    extract = Api_History['date'] >= datetime.now() - timedelta(days=31)
    api_from_less_than_or_equal_month = Api_History[extract]
    print("read_api_from_less_than_or_equal_month are readed")
    return api_from_less_than_or_equal_month

def read_the_api_file_and_add_requests(Api_from_more_than_month_df):
    with open(api_file_path, 'r') as file:
        apis = json.load(file)
    final_api = []
    # Update Available_requests_per_month for matching APIs
    for main_api in apis:
        for index, used_api in Api_from_more_than_month_df.iterrows():
            if (main_api['url'] == used_api['url'] 
                and main_api['x-rapidapi-key'] == used_api['x-rapidapi-key'] 
                and main_api['x-rapidapi-host'] == used_api['x-rapidapi-host']):
                main_api['Avilabe_requests_per_month'] = int(main_api.get('Avilabe_requests_per_month', 0)) + int(used_api['used'])
        
        final_api.append(main_api)
    print(final_api)
    # Write updated data back to the JSON file
    with open(api_file_path, 'w') as file:
        json.dump(final_api, file, indent=4)
        print("API file is modified")

def write_the_new_api_history(api_from_less_than_or_equal_month):
    api_from_less_than_or_equal_month.to_csv(api_history_file_path, mode='w', header=True, index=False)
    print("API_history file is modified")

# Define tasks
def task_read_api_history(**kwargs):
    Api_History = read_api_history()
    kwargs['ti'].xcom_push(key='Api_History', value=Api_History)

def task_read_api_from_more_than_month(**kwargs):
    Api_History = kwargs['ti'].xcom_pull(key='Api_History', task_ids='read_api_history')
    Api_from_more_than_month = read_api_from_more_than_month(Api_History)
    kwargs['ti'].xcom_push(key='Api_from_more_than_month', value=Api_from_more_than_month)

def task_read_api_from_less_than_or_equal_month(**kwargs):
    Api_History = kwargs['ti'].xcom_pull(key='Api_History', task_ids='read_api_history')
    api_from_less_than_or_equal_month = read_api_from_less_than_or_equal_month(Api_History)
    kwargs['ti'].xcom_push(key='api_from_less_than_or_equal_month', value=api_from_less_than_or_equal_month)

def task_read_the_api_file_and_add_requests(**kwargs):
    Api_from_more_than_month_df = kwargs['ti'].xcom_pull(key='Api_from_more_than_month', task_ids='read_api_from_more_than_month')
    read_the_api_file_and_add_requests(Api_from_more_than_month_df)

def task_write_the_new_api_history(**kwargs):
    api_from_less_than_or_equal_month = kwargs['ti'].xcom_pull(key='api_from_less_than_or_equal_month', task_ids='read_api_from_less_than_or_equal_month')
    write_the_new_api_history(api_from_less_than_or_equal_month)

# Create tasks
read_api_history_task = PythonOperator(
    task_id='read_api_history',
    python_callable=task_read_api_history,
    dag=dag,
)

read_api_from_more_than_month_task = PythonOperator(
    task_id='read_api_from_more_than_month',
    python_callable=task_read_api_from_more_than_month,
    dag=dag,
)

read_api_from_less_than_or_equal_month_task = PythonOperator(
    task_id='read_api_from_less_than_or_equal_month',
    python_callable=task_read_api_from_less_than_or_equal_month,
    dag=dag,
)

read_the_api_file_and_add_requests_task = PythonOperator(
    task_id='read_the_api_file_and_add_requests',
    python_callable=task_read_the_api_file_and_add_requests,
    dag=dag,
)

write_the_new_api_history_task = PythonOperator(
    task_id='write_the_new_api_history',
    python_callable=task_write_the_new_api_history,
    dag=dag,
)

# Define dependencies
read_api_history_task >> [read_api_from_more_than_month_task, read_api_from_less_than_or_equal_month_task]
read_api_from_more_than_month_task >> read_the_api_file_and_add_requests_task
read_api_from_less_than_or_equal_month_task >> write_the_new_api_history_task
