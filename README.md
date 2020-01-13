# Project: Data Pipelines

## Intro

The goal of the project is to use Apache Airflow to define, run and monitor an ETL pipeline with Apache Airflow. 

The events and songs raw data is loaded from Amazon S3, transformed and stored on RedShift into a suitable data model 
which enables the Sparkify team to design and execute their analytics queries.

The README presents the following:
1. Pipeline description
2. Custom operators
2. Pre-requisites
3. How to execute the ETL


## Pipeline Description

The pipeline designed as part of this project loads the data from S3 into Redshift, transforms it using SQL statements
and creates a data model based on the the Star schema principles.

There are several tasks involved which use a combination of existing Airflow operators and custom ones.
The custom operators (see below) have been provided to abstract repeatable and reusable functions.

The artifacts defining the pipelines are:
- `airflow/dags/udac_example_dag.py` contains the definition of the DAG and its tasks
- `airflow/dags/create_tables.sql` creates the data model (staging, fact and dimensions tables)
- `airflow/plugins/helpers/sql_queries.sql` containts the statements to perform the SQL transformations
- `airflow/plugins/operators` folder with the 4 custom operators
 
 The create_tables.sql only creates the tables when they do not exist, therefore it can be run every time the pipeline
 is executed

## Custom operators

During the design of the pipelines 4 Aiflow custom operators have been created. The operators are meant to be
generic and re-usable in different tasks of the same pipeline or even across different pipelines.

### StageToRedshiftOperator

The 'StageToRedshiftOperator' loads the JSON data from S3 and stores in a staging table: this operator has been
designed with the assumption that raw data is always in JSON format (another operator could be developed to support
other formats i.e. CSV) 

### LoadFactOperator

The 'LoadFactOperator' creates a Fact table: it loads the data from the given staging table, performs 
the required transformation and stores the output in the designated Fact table 

### LoadDimensionOperator

The 'LoadDimensionOperator' creates a Dimension table: it loads the data from the given staging table, performs 
the required transformation and stores the output in the designated Dimension table 

### DataQualityOperator

The 'DataQualityOperator' enables the validation of the data created by the pipeline: the operator allows to 
check if a given column in a given table contains records which are not null  

## Pre-requisites

In order to execute the pipeline the following steps are required:

- Start RedShift cluster (note down attributes as they are required during the Airflow setup)
- Start Airflow from the root directory (/opt/airflow/start.sh)
- In Airflow Administration create an 'Amazon Web Service' connection, see the following as an example
    - Conn Id: aws_credentials
    - Conn Type: Amazon Web Services 
    - Login: ```<AWS Key>```
    - Password: ```<AWS Secret>```
- In Airflow Administration create an 'Postgres' connection, see the following as an example
    - Conn Id: redshift
    - Conn Type: postgres
    - Host: ```<Redshift Cluster host>```
    - Schema: dev
    - Login: ```<Redshift Cluster Master Username>```
    - Password: ```<Redshift Cluster Master Password>```
    - Port: 5439


## Execute the ETL


For this project, you'll be working with two datasets. Here are the s3 links for each:

Log data: s3://udacity-dend/log_data
Song data: s3://udacity-dend/song_data

## Configuring the DAG
In the DAG, add default parameters according to these guidelines

The DAG does not have dependencies on past runs
On failure, the task are retried 3 times
Retries happen every 5 minutes
Catchup is turned off
Do not email on retry

## Building the operators
To complete the project, you need to build four different operators that will stage the data, transform the data, and 
run checks on data quality.

You can reuse the code from Project 2, but remember to utilize Airflow's built-in functionalities as connections and 
hooks as much as possible and let Airflow do all the heavy-lifting when it is possible.

All of the operators and task instances will run SQL statements against the Redshift database. However, using parameters 
wisely will allow you to build flexible, reusable, and configurable operators you can later apply 
to many kinds of data pipelines with Redshift and with other databases.

## Stage Operator
The stage operator is expected to be able to load any JSON formatted files from S3 to Amazon Redshift. The operator 
creates and runs a SQL COPY statement based on the parameters provided. The operator's parameters should specify where 
in S3 the file is loaded and what is the target table.

The parameters should be used to distinguish between JSON file. Another important requirement of the stage operator is 
containing a templated field that allows it to load timestamped files from S3 based on the execution time and run backfills.

## Fact and Dimension Operators
With dimension and fact operators, you can utilize the provided SQL helper class to run data transformations. Most of 
the logic is within the SQL transformations and the operator is expected to take as input a SQL statement and target 
database on which to run the query against. You can also define a target table that will contain the results of the 
transformation.

Dimension loads are often done with the truncate-insert pattern where the target table is emptied before the load. 
Thus, you could also have a parameter that allows switching between insert modes when loading dimensions. Fact tables 
are usually so massive that they should only allow append type functionality.

## Data Quality Operator
The final operator to create is the data quality operator, which is used to run checks on the data itself. The operator's 
main functionality is to receive one or more SQL based test cases along with the expected results and execute the tests. 
For each the test, the test result and expected result needs to be checked and if there is no match, the operator should 
raise an exception and the task should retry and fail eventually.

For example one test could be a SQL statement that checks if certain column contains NULL values by counting all the rows 
that have NULL in the column. We do not want to have any NULLs so expected result would be 0 and the test would compare 
the SQL statement's outcome to the expected result.

