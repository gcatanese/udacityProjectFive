from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator,
                               LoadDimensionOperator, DataQualityOperator)
from airflow.operators.postgres_operator import PostgresOperator
from airflow.helpers import sql_queries as SqlQueries

# AWS_KEY = os.environ.get('AWS_KEY')
# AWS_SECRET = os.environ.get('AWS_SECRET')

default_args = {
    'owner': 'udacity',
    'start_date': datetime(2019, 1, 12),
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_retry': False
}

dag = DAG('udac_example_dag',
          catchup=False,
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='0 * * * *'
          )

start_operator = DummyOperator(task_id='Begin_execution', dag=dag)

# Create staging SONGS on Redshift
create_staging_songs_table_task = PostgresOperator(
    task_id="create_staging_songs_table",
    dag=dag,
    postgres_conn_id="redshift",
    sql="""CREATE TABLE IF NOT EXISTS public.staging_songs (
    num_songs INT4,
    artist_id VARCHAR(256),
    artist_name VARCHAR(256),
    artist_latitude NUMERIC(18,0),
    artist_longitude NUMERIC(18,0),
    artist_location VARCHAR(256),
    song_id VARCHAR(256),
    title VARCHAR(256),
    duration NUMERIC(18,0),
    \"year\" INT4);"""
)

# Create staging EVENTS on Redshift
create_staging_events_table_task = PostgresOperator(
    task_id="create_staging_events_table",
    dag=dag,
    postgres_conn_id="redshift",
    sql="""CREATE TABLE IF NOT EXISTS public.staging_events (
    artist VARCHAR(256),
    auth VARCHAR(256),
    firstname VARCHAR(256),
    gender VARCHAR(256),
    iteminsession INT4,
    lastname VARCHAR(256),
    length NUMERIC(18,0),
    \"level\" VARCHAR(256),
    location VARCHAR(256),
    \"method\" VARCHAR(256),
    page VARCHAR(256),
    registration NUMERIC(18,0),
    sessionid INT4,
    song VARCHAR(256),
    status INT4,
    ts INT8,
    useragent VARCHAR(256),
    userid INT4
    """
)

stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    dag=dag
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    dag=dag
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    dag=dag
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag
)

run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag
)

end_operator = DummyOperator(task_id='Stop_execution', dag=dag)
