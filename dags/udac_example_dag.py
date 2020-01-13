from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator,
                               LoadDimensionOperator, DataQualityOperator)
from helpers import SqlQueries

from airflow.operators import PostgresOperator

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

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

# Create staging, fact and dimensions tables on Redshift
create_tables = PostgresOperator(
    task_id="create_tables",
    dag=dag,
    postgres_conn_id="redshift",
    sql="create_tables.sql"
)

# Load events on staging
stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    dag=dag,
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",
    s3_bucket="udacity-dend",
    s3_key="log_data",
    format_as_json='s3://udacity-dend/log_json_path.json',
    table="staging_events"
)

# Load songs on staging
stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag,
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",
    s3_bucket="udacity-dend",
    s3_key="song_data",
    format_as_json='auto',
    table="staging_songs"
)

# Load Fact table
load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag,
    redshift_conn_id="redshift",
    table_name="songplays",
    sql_select_stmt=SqlQueries.songplay_table_insert
)

# Load Dimension table
load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag,
    redshift_conn_id="redshift",
    table_name="users",
    sql_select_stmt=SqlQueries.user_table_insert
)

# Load Dimension table
load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    dag=dag,
    redshift_conn_id="redshift",
    table_name="songs",
    sql_select_stmt=SqlQueries.song_table_insert
)

# Load Dimension table
load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    dag=dag,
    redshift_conn_id="redshift",
    table_name="artists",
    sql_select_stmt=SqlQueries.artist_table_insert
)

# Load Dimension table
load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag,
    redshift_conn_id="redshift",
    table_name="time",
    sql_select_stmt=SqlQueries.time_table_insert
)

# Validate 'time.hour' column not empty
run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag,
    redshift_conn_id="redshift",
    table="time",
    column="hour"
)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)

# Define tasks order
start_operator >> create_tables
create_tables >> stage_events_to_redshift
create_tables >> stage_songs_to_redshift
stage_events_to_redshift >> load_songplays_table
stage_songs_to_redshift >> load_songplays_table
load_songplays_table >> load_user_dimension_table
load_songplays_table >> load_song_dimension_table
load_songplays_table >> load_artist_dimension_table
load_songplays_table >> load_time_dimension_table
load_user_dimension_table >> run_quality_checks
load_song_dimension_table >> run_quality_checks
load_artist_dimension_table >> run_quality_checks
load_time_dimension_table >> run_quality_checks
run_quality_checks >> end_operator
