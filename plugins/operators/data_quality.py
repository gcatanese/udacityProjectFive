from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):
    """
    Performs data quality checks to verify the given table is not empty

    :param redshift_conn_id: Redshift connection ID
    :param table: Table name
    :param column: Column name
    """

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 table="",
                 column="",
                 *args, **kwargs):
        """
        Initialise the operator

        :param redshift_conn_id: Redshift connection ID
        :param table: Table name
        :param column: Column name
        """

        super(DataQualityOperator, self).__init__(*args, **kwargs)

        self.redshift_conn_id = redshift_conn_id
        self.table = table
        self.column = column

    def execute(self, context):
        """
        Executes the operator logic

        :param context:
        """

        self.log.info(f'Validating table {self.table}')

        redshift_hook = PostgresHook(self.redshift_conn_id)
        records = redshift_hook.get_records(f"SELECT COUNT(*) FROM {self.table} WHERE {self.column} IS NOT NULL")
        if len(records) < 1 or len(records[0]) < 1:
            raise ValueError(f"Data quality check failed. Table '{self.table}' contained no row")
        num_records = records[0][0]
        if num_records < 1:
            raise ValueError(f"Data quality check failed. Table '{self.table}' contained no rows")

        self.log.info(f"Data quality on table '{self.table}' check passed: found {records[0][0]} records")