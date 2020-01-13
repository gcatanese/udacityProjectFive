from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

from airflow.contrib.hooks.aws_hook import AwsHook

class StageToRedshiftOperator(BaseOperator):
    """
    Copies the data from S3 into the staging table

        :param redshift_conn_id: Redshift connection ID
        :param aws_credentials_id: AWS connection ID
        :param table: Name of the staging table
        :param s3_bucket: Name of the bucket with the JSON data
        :param s3_key: Path of the JSON files within the bucket
        :param format_as_json: Value of FORMAT_AS_JSON option: 'auto' for auto mapping, path to JSONPaths file
    """

    ui_color = '#358140'

    template_fields = ("s3_key",)
    copy_sql = """
        COPY {}
        FROM '{}'
        ACCESS_KEY_ID '{}'
        SECRET_ACCESS_KEY '{}'
        FORMAT AS JSON '{}'
        TIMEFORMAT as 'epochmillisecs'
        COMPUPDATE OFF
    """

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 aws_credentials_id="",
                 table="",
                 s3_bucket="",
                 s3_key="",
                 format_as_json=",",
                 *args, **kwargs):
        """
        Initialise the operator

        :param redshift_conn_id: Redshift connection ID
        :param aws_credentials_id: AWS connection ID
        :param table: Name of the staging table
        :param s3_bucket: Name of the bucket with the JSON data
        :param s3_key: Path of the JSON files within the bucket
        :param format_as_json: Value of FORMAT_AS_JSON option: 'auto' for auto mapping, path to JSONPaths file
        """

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)

        self.table = table
        self.redshift_conn_id = redshift_conn_id
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.format_as_json = format_as_json
        self.aws_credentials_id = aws_credentials_id

    def execute(self, context):
        """
        Executes the operator logic

        :param context:
        """

        self.log.info('StageToRedshiftOperator execute')

        aws_hook = AwsHook(self.aws_credentials_id)
        credentials = aws_hook.get_credentials()
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        self.log.info("Clearing data from destination Redshift table")
        redshift.run("DELETE FROM {}".format(self.table))

        self.log.info("Copying data from S3 to Redshift")
        rendered_key = self.s3_key.format(**context)
        s3_path = "s3://{}/{}".format(self.s3_bucket, rendered_key)
        self.log.info('StageToRedshiftOperator s3_path: ' + s3_path)
        formatted_sql = StageToRedshiftOperator.copy_sql.format(
            self.table,
            s3_path,
            credentials.access_key,
            credentials.secret_key,
            self.format_as_json
        )
        redshift.run(formatted_sql)