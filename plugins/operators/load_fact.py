from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadFactOperator(BaseOperator):
    """
    Loads the Fact table

    :param redshift_conn_id: Redshift connection ID
    :param table_name: Table name
    :param sql_select_stmt: SQL statement which performs the loading of the data
    """

    ui_color = '#F98866'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 table_name="",
                 sql_select_stmt="",
                 *args, **kwargs):
        """
        Initialise the operator

        :param redshift_conn_id: Redshift connection ID
        :param table_name: Table name
        :param sql_select_stmt: SQL statement which performs the loading of the data
        """

        super(LoadFactOperator, self).__init__(*args, **kwargs)

        self.redshift_conn_id = redshift_conn_id
        self.table_name = table_name
        self.sql_select_stmt = sql_select_stmt


    def execute(self, context):
        """
        Executes the operator logic

        :param context:
        """

        self.log.info('Loading Fact table ' + self.table_name)

        redshift_hook = PostgresHook(self.redshift_conn_id)

        sql_stmt = "TRUNCATE {} "
        formatted_sql_stmt = sql_stmt.format(self.table_name)
        self.log.info(formatted_sql_stmt)
        redshift_hook.run(formatted_sql_stmt)

        sql_stmt = "INSERT INTO {} {}"
        formatted_sql_stmt = sql_stmt.format(self.table_name, self.sql_select_stmt)
        self.log.info(formatted_sql_stmt)

        redshift_hook.run(formatted_sql_stmt)
