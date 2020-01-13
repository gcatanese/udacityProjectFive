# Project: Data Pipelines

## Intro

The goal of the project is to use Apache Airflow to define, run and monitor an ETL pipeline with Apache Airflow. 

The raw data is loaded from Amazon S3, transformed and stored onto RedShift in a suitable data model 
which enables the Sparkify team to design and execute their analytics queries.


## Pipeline Description

The pipeline designed as part of this project loads the data from S3 into Redshift, transforms it using SQL statements
and eventually creates a data model based on the the Star schema principles.

There are several tasks involved which use a combination of existing Airflow operators and custom ones.
The custom operators (see below) have been provided to abstract repeatable and reusable functions.

### Pipeline Components
The artifacts defining the pipelines are:
- `airflow/dags/udac_example_dag.py` contains the definition of the DAG and its tasks
- `airflow/dags/create_tables.sql` creates the data model (staging, fact and dimensions tables)
- `airflow/plugins/helpers/sql_queries.sql` containts the statements to perform the SQL transformations
- `airflow/plugins/operators` folder with the 4 custom operators
 
 The create_tables.sql creates the tables only when they do not yet exist, therefore it runs every time the pipeline
 is executed.
 
 The pipeline validates that column 'hour' in table 'time' is not empty: other validations could be added (re-using
 the same operator) on other tables/columns

## Custom operators

During the design of the pipelines 4 Aiflow custom operators have been created. The operators are meant to be
generic and reused in different tasks of the same pipeline or even across different pipelines.

### StageToRedshiftOperator

The 'StageToRedshiftOperator' loads the JSON data from S3 and stores in a staging table: this operator has been
designed with the assumption that raw data is always in JSON format (another operator could be developed to support
other formats i.e. CSV) 

### LoadFactOperator

The 'LoadFactOperator' creates a Fact table: it loads the data from the given staging table, performs 
the required transformation and stores the output in the designated Fact table.

### LoadDimensionOperator

The 'LoadDimensionOperator' creates a Dimension table: it loads the data from the given staging table, performs 
the required transformation and stores the output in the designated Dimension table.

### DataQualityOperator

The 'DataQualityOperator' enables the validation of the data created by the pipeline: the operator allows to 
check if a given column in a given table contains records which are not null .

## Pre-requisites

In order to execute the pipeline the following steps are required:

- Start a RedShift cluster (note down attributes as they are required during the Airflow setup)
- Start Airflow from the root directory (/opt/airflow/start.sh)
- In Airflow Administration create an 'Amazon Web Service' connection, see the following as an example:
    - Conn Id: aws_credentials
    - Conn Type: Amazon Web Services 
    - Login: ```<AWS Key>```
    - Password: ```<AWS Secret>```
- In Airflow Administration create a 'Postgres' connection, see the following as an example:
    - Conn Id: redshift
    - Conn Type: postgres
    - Host: ```<Redshift Cluster host>```
    - Schema: dev
    - Login: ```<Redshift Cluster Master Username>```
    - Password: ```<Redshift Cluster Master Password>```
    - Port: 5439


## Execute the ETL

In Airflow enables the `udac_example_dag` DAG 

