import os
import logging
import pyodbc
import requests
import tempfile
import pandas as pd
import zipfile
import re

from github import Github
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth

from airflow import DAG, settings
from airflow.utils.dates import days_ago
from airflow.models import Variable, Connection

################################### OPERATORS ###########################################################

from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.sensors.python import PythonSensor
from airflow.operators.bash import BashOperator

from airflow.providers.microsoft.azure.operators.data_factory import AzureDataFactoryRunPipelineOperator
from airflow.providers.microsoft.azure.sensors.data_factory import AzureDataFactoryPipelineRunStatusSensor
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator
from airflow.providers.microsoft.azure.operators.adls import ADLSListOperator

################################### VARIABLES ###########################################################

BINANCE_API_LINK = 'https://api.binance.com/api/v3/ticker/price'

SERVER = os.getenv('SERVER','sqlserver-vinietlazure.database.windows.net')
DATABASE = os.getenv('DATABASE','database-sqlserver-vinietlazure')
LOGIN = os.getenv('LOGIN','vinietlazure')
PASSWORD = Variable.get("PASSWORD")
DRIVER = os.getenv('DRIVER','{ODBC Driver 17 for SQL Server}')
CONN_SQL_SERVER_DATABASE = 'DRIVER='+DRIVER+'; SERVER=tcp:'+SERVER+';PORT=1433;DATABASE='+DATABASE+';UID='+LOGIN+';PWD='+PASSWORD

GITHUB_TOKEN = Variable.get("GITHUB_TOKEN")
GITHUB_USER = os.getenv("GITHUB_USER", "camposvinicius")
GITHUB_REPO = os.getenv("GITHUB_REPO", "azure-etl")
GITHUB_WORKFLOW_FILE_NAME_1 = os.getenv('GITHUB_WORKFLOW_FILE_NAME_1', 'resources1.yml')
GITHUB_WORKFLOW_FILE_NAME_2 = os.getenv('GITHUB_WORKFLOW_FILE_NAME_2', 'resources2.yml')
GITHUB_WORKFLOW_FILE_DESTROY = os.getenv('GITHUB_WORKFLOW_FILE_DESTROY', 'destroy.yml')
GITHUB_URL_LOGS_WORKFLOW="https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/actions/runs/{MAX_ID}/logs"

ADF_RESOURCE_GROUP_NAME = os.getenv('ADF_RESOURCE_GROUP_NAME', 'vinietlazure')
ADF_FACTORY_NAME = os.getenv('ADF_FACTORY_NAME', 'vinidatafactoryazure')
ADF_TENANT_ID = os.getenv('ADF_TENANT_ID', 'your-tenant-ID')
ADF_SUBSCRIPTION_ID = os.getenv('ADF_SUBSCRIPTION_ID', 'your-subscription-ID')

NOTEBOOK_BRONZETOSILVER = {"notebook_path": "/ViniEtlAzure/Notebooks/bronzeToSilver.dbc"}
NOTEBOOK_SILVERTOGOLD = {"notebook_path": "/ViniEtlAzure/Notebooks/silverToGold.dbc"}
NOTEBOOK_GOLDTOCOSMOSDB = {"notebook_path": "/ViniEtlAzure/Notebooks/goldToCosmosdb.dbc"}
NOTEBOOK_GOLDTOSYNAPSE = {"notebook_path": "/ViniEtlAzure/Notebooks/goldToSynapse.dbc"}

################################### FUNCTIONS ###########################################################

def get_and_inject_data_on_sql_server():
    with tempfile.TemporaryDirectory() as temp_path:
        temp_dir = os.path.join(temp_path, 'data')
        with open(temp_dir, 'wb') as f:
            x = True
            timer = datetime.now()
            frames = []

            while x:
                if datetime.now() - timer > timedelta(seconds=180):
                    x = False
                req = requests.get(BINANCE_API_LINK)

                df = pd.read_json(req.content)
                frames.append(df)

            df = pd.concat(frames)
            df = df.loc[df['symbol'].isin(['BTCUSDT', 'ADAUSDT', 'ETHUSDT', 'BNBUSDT', 'LTCUSDT'])]
            df = df.sort_values(by=['symbol'])

            with pyodbc.connect(CONN_SQL_SERVER_DATABASE) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('''
                    
                        DROP TABLE IF EXISTS dbo.crypto
                        
                        CREATE TABLE dbo.crypto (
                            symbol varchar(10) not null,
                            price decimal(10, 2) not null
                        )                   
                    
                    ''')

                for index, row in df.iterrows():
                    cursor.execute(f'''
                        INSERT INTO crypto (
                            symbol, 
                            price
                        ) 
                        VALUES (
                            '{row.symbol}',
                            {row.price}
                        ) 
                        ''')

def run_github_workflow_action(task_id, action, workflow_filename):
    return BashOperator(
        task_id=f'{task_id}',
        bash_command="""
            curl \
                -X POST \
                -H "Authorization: Token {{ params.GITHUB_TOKEN }} " \
                https://api.github.com/repos/{{ params.GITHUB_USER }}/{{ params.GITHUB_REPO }}/actions/workflows/{{ params.GITHUB_WORKFLOW_FILE_NAME }}/dispatches \
                -d '{"ref":"main", "inputs": { "action": "{{ params.ACTION }}" }}'
        """,
        params={
            'GITHUB_TOKEN': GITHUB_TOKEN,
            'ACTION': f'{action}',
            'GITHUB_USER': GITHUB_USER,
            'GITHUB_REPO': GITHUB_REPO,
            'GITHUB_WORKFLOW_FILE_NAME': f'{workflow_filename}',
        }
    )

def get_last_status_last_workflow(**kwargs):

  g = Github(GITHUB_TOKEN)

  repo = g.get_repo(f"{GITHUB_USER}/{GITHUB_REPO}")
  workflows = repo.get_workflow_runs(actor=GITHUB_USER, branch='main')

  ids = []
  for i in workflows:
    ids.append(str(i).split(",")[-1].split("=")[-1].split(")")[0])

  max_workflow = int(max(ids))

  last_workflow = repo.get_workflow_run(max_workflow)

  ti = kwargs['ti']    
  ti.xcom_push(key='last_status_last_workflow', value=f'{last_workflow.id}')

  if last_workflow.conclusion != 'success':
    return False
  else:
    return True

def download_github_action_logs(id_workflow: int, metric: str, **kwargs):
    
    response = requests.get(
        GITHUB_URL_LOGS_WORKFLOW.format(
            GITHUB_USER=GITHUB_USER, 
            GITHUB_REPO=GITHUB_REPO, 
            MAX_ID=id_workflow
        ),
        auth=HTTPBasicAuth(
            GITHUB_USER, 
            GITHUB_TOKEN)
    )

    with open('logs.zip', 'wb') as f:
        f.write(response.content)
        with zipfile.ZipFile("logs.zip","r") as zip_ref:
            zip_ref.extractall()

        file_path = []
        for file in os.listdir():
            if file.endswith(".txt"):
                file_path.append(f"{file}")

        for x in file_path:
            with open(x, encoding='utf8') as f:
                contents = f.read()
            
            i = re.findall(fr"{metric}", contents)
            f = re.findall(fr"{metric}(.*)", contents)

            for k,v in zip(i, f):
                var_k = k.strip()
                var_v = v.strip()[3:-1].replace('"', "").replace(" ", "")

        ti = kwargs['ti']
        ti.xcom_push(key=f'{var_k}', value=f'{var_v}')

def create_conn(conn_id, conn_type, extra=None, login=None, password=None, host=None, port=None, desc=None):
    conn = Connection(
        conn_id=conn_id,
        conn_type=conn_type,
        extra=extra,
        login=login,
        password=password,
        host=host,
        port=port,
        description=desc
    )

    session = settings.Session()
    conn_name = session.query(Connection).filter(Connection.conn_id == conn.conn_id).first()

    if str(conn_name) == str(conn.conn_id):
        logging.warning(f"Connection {conn.conn_id} already exists")
        return None

    session.add(conn)
    session.commit()
    logging.info(Connection.log_info(conn))
    logging.info(f'Connection {conn_id} is created')
    return conn

def run_databricks_notebook(task_id, databricks_cluster_id, notebook_task):
    return DatabricksSubmitRunOperator(
        task_id=task_id,
        existing_cluster_id=databricks_cluster_id,
        notebook_task=notebook_task,
        databricks_conn_id='azure_databricks'
    )

################################### TASKS ###############################################################

default_args = {
    'owner': 'Vinicius Campos',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1
}

with DAG(
    dag_id="vini-campos-etl-azure",
    tags=['etl', 'azure', 'dataengineer'],
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval='@daily',
    catchup=False
) as dag:

    github_workflow_action_constroy_terraform_resources_1 = run_github_workflow_action(
        'github_workflow_action_constroy_terraform_resources_1',
        GITHUB_WORKFLOW_FILE_NAME_1[:-4],
        GITHUB_WORKFLOW_FILE_NAME_1
    )

    poke_github_workflow_status_terraform_resources_1 = PythonSensor(
        task_id='poke_github_workflow_status_terraform_resources_1',
        python_callable=get_last_status_last_workflow
    )

    task_get_and_inject_data_on_sql_server = PythonOperator(
        task_id='get_and_inject_data_on_sql_server',
        python_callable=get_and_inject_data_on_sql_server
    )

    github_workflow_action_constroy_terraform_resources_2 = run_github_workflow_action(
        'github_workflow_action_constroy_terraform_resources_2',
        GITHUB_WORKFLOW_FILE_NAME_2[:-4],
        GITHUB_WORKFLOW_FILE_NAME_2
    )

    poke_github_workflow_status_terraform_resources_2 = PythonSensor(
        task_id='poke_github_workflow_status_terraform_resources_2',
        python_callable=get_last_status_last_workflow
    )

    download_github_action_logs_resources_2_clientID_ADF = PythonOperator(
        task_id='download_github_action_logs_resources_2_clientID_ADF',
        python_callable=download_github_action_logs,
        op_args=[
            "{{ task_instance.xcom_pull(task_ids='poke_github_workflow_status_terraform_resources_2', key='last_status_last_workflow') }}",
            "clientID"
        ],
        provide_context=True
    )

    download_github_action_logs_resources_2_secret_ADF = PythonOperator(
        task_id='download_github_action_logs_resources_2_secret_ADF',
        python_callable=download_github_action_logs,
        op_args=[
            "{{ task_instance.xcom_pull(task_ids='poke_github_workflow_status_terraform_resources_2', key='last_status_last_workflow') }}",
            "Secret"
        ],
        provide_context=True
    )

    download_github_action_logs_resources_2_host_databricks = PythonOperator(
        task_id='download_github_action_logs_resources_2_host_databricks',
        python_callable=download_github_action_logs,
        op_args=[
            "{{ task_instance.xcom_pull(task_ids='poke_github_workflow_status_terraform_resources_2', key='last_status_last_workflow') }}",
            "host"
        ],
        provide_context=True
    )

    download_github_action_logs_resources_2_token_databricks = PythonOperator(
        task_id='download_github_action_logs_resources_2_token_databricks',
        python_callable=download_github_action_logs,
        op_args=[
            "{{ task_instance.xcom_pull(task_ids='poke_github_workflow_status_terraform_resources_2', key='last_status_last_workflow') }}",
            "token"
        ],
        provide_context=True
    )

    download_github_action_logs_resources_2_clusterID_databricks = PythonOperator(
        task_id='download_github_action_logs_resources_2_clusterID_databricks',
        python_callable=download_github_action_logs,
        op_args=[
            "{{ task_instance.xcom_pull(task_ids='poke_github_workflow_status_terraform_resources_2', key='last_status_last_workflow') }}",
            "ClusterId"
        ],
        provide_context=True
    )

    task_dummy = DummyOperator(
        task_id='task_dummy'
    )

    add_conn_adf = PythonOperator(
        task_id='add_conn_adf',
        python_callable=create_conn,
        op_args=[
            'azure_data_factory_conn_id',
            'Azure Data Factory',
            {
                "extra__azure_data_factory__resource_group_name" : ADF_RESOURCE_GROUP_NAME,
                "extra__azure_data_factory__factory_name" : ADF_FACTORY_NAME,
                "extra__azure_data_factory__tenantId" : ADF_TENANT_ID,
                "extra__azure_data_factory__subscriptionId" : ADF_SUBSCRIPTION_ID
            },
            "{{ task_instance.xcom_pull(task_ids='download_github_action_logs_resources_2_clientID_ADF', key='clientID') }}",
            "{{ task_instance.xcom_pull(task_ids='download_github_action_logs_resources_2_secret_ADF', key='Secret') }}"
        ]
    )

    add_conn_databricks = PythonOperator(
        task_id='add_conn_databricks',
        python_callable=create_conn,
        op_args=[
            'azure_databricks',
            'Databricks',
            {
                "token": "{{ task_instance.xcom_pull(task_ids='download_github_action_logs_resources_2_token_databricks', key='token') }}",
                "host": "{{ task_instance.xcom_pull(task_ids='download_github_action_logs_resources_2_host_databricks', key='host') }}"
            },
            'token'
        ]
    )

    run_ADF_pipeline = AzureDataFactoryRunPipelineOperator(
        task_id='run_ADF_pipeline_CopySqlServerToBronzeBlobContainer',
        pipeline_name='CopySqlServerToBronzeBlobContainer',
        wait_for_termination=True,
        azure_data_factory_conn_id='azure_data_factory_conn_id'
    )

    status_ADF_pipeline = AzureDataFactoryPipelineRunStatusSensor(
        task_id='status_ADF_pipeline_CopySqlServerToBronzeBlobContainer',
        run_id=run_ADF_pipeline.output["run_id"],
        azure_data_factory_conn_id='azure_data_factory_conn_id'
    )

    databricks_notebook_bronze2silver = run_databricks_notebook(
        task_id='databricks_notebook_bronze2silver',
        databricks_cluster_id="{{ task_instance.xcom_pull(task_ids='download_github_action_logs_resources_2_clusterID_databricks', key='ClusterId') }}",
        notebook_task=NOTEBOOK_BRONZETOSILVER
    )

    databricks_notebook_silver2gold = run_databricks_notebook(
        task_id='databricks_notebook_silver2gold',
        databricks_cluster_id="{{ task_instance.xcom_pull(task_ids='download_github_action_logs_resources_2_clusterID_databricks', key='ClusterId') }}",
        notebook_task=NOTEBOOK_SILVERTOGOLD
    )

    databricks_notebook_gold2cosmosdb = run_databricks_notebook(
        task_id='databricks_notebook_gold2cosmosdb',
        databricks_cluster_id="{{ task_instance.xcom_pull(task_ids='download_github_action_logs_resources_2_clusterID_databricks', key='ClusterId') }}",
        notebook_task=NOTEBOOK_GOLDTOCOSMOSDB
    )

    databricks_notebook_gold2synapse = run_databricks_notebook(
        task_id='databricks_notebook_gold2synapse',
        databricks_cluster_id="{{ task_instance.xcom_pull(task_ids='download_github_action_logs_resources_2_clusterID_databricks', key='ClusterId') }}",
        notebook_task=NOTEBOOK_GOLDTOSYNAPSE
    )

    github_workflow_action_destroy_all_resources = run_github_workflow_action(
        'github_workflow_action_destroy_all_resources',
        GITHUB_WORKFLOW_FILE_DESTROY[:-4],
        GITHUB_WORKFLOW_FILE_DESTROY
    )

    poke_github_workflow_status_destroy_terraform_resources = PythonSensor(
        task_id='poke_github_workflow_status_destroy_terraform_resources',
        python_callable=get_last_status_last_workflow
    )

    (         
        github_workflow_action_constroy_terraform_resources_1 >> poke_github_workflow_status_terraform_resources_1 >>
        
        task_get_and_inject_data_on_sql_server >>

        github_workflow_action_constroy_terraform_resources_2 >> poke_github_workflow_status_terraform_resources_2 >> 
        
        [download_github_action_logs_resources_2_clientID_ADF, download_github_action_logs_resources_2_secret_ADF, download_github_action_logs_resources_2_host_databricks, download_github_action_logs_resources_2_token_databricks, download_github_action_logs_resources_2_clusterID_databricks] >>
        
        task_dummy >> [add_conn_adf, add_conn_databricks] >> run_ADF_pipeline >> status_ADF_pipeline >>

        databricks_notebook_bronze2silver >> databricks_notebook_silver2gold >> [databricks_notebook_gold2cosmosdb, databricks_notebook_gold2synapse] >>
        
        github_workflow_action_destroy_all_resources >> poke_github_workflow_status_destroy_terraform_resources
    
    )