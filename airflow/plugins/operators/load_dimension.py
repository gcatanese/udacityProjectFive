from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadDimensionOperator(BaseOperator):

    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 table_name="",
                 sql_select_stmt="",
                 *args, **kwargs):

        super(LoadDimensionOperator, self).__init__(*args, **kwargs)

        self.redshift_conn_id = redshift_conn_id
        self.table_name = table_name
        self.sql_select_stmt = sql_select_stmt

    def execute(self, context):
        self.log.info('Loading Dimension table')

        redshift_hook = PostgresHook(self.redshift_conn_id)

        sql_stmt = "INSERT INTO {} {}"
        formatted_sql_stmt = sql_stmt.format(self.table_name, self.sql_select_stmt)

        redshift_hook.run(formatted_sql_stmt)

