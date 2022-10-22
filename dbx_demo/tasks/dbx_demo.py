from dbx_demo.common import Task, print_thing
from pyspark.sql.types import *
from datetime import date
import pandas as pd


class DbxDemoTask(Task):
    def _run_dbx_demo(self):
        print_thing("cheeeese!")
        # Create a DataFrame consisting of high and low temperatures
        # by airport code and date.
        schema = StructType([
        StructField('AirportCode', StringType(), False),
        StructField('Date', DateType(), False),
        StructField('TempHighF', IntegerType(), False),
        StructField('TempLowF', IntegerType(), False)
        ])

        data = [
        [ 'BLI', date(2021, 4, 3), 52, 43],
        [ 'BLI', date(2021, 4, 2), 50, 38],
        [ 'BLI', date(2021, 4, 1), 52, 41],
        [ 'PDX', date(2021, 4, 3), 64, 45],
        [ 'PDX', date(2021, 4, 2), 61, 41],
        [ 'PDX', date(2021, 4, 1), 66, 39],
        [ 'SEA', date(2021, 4, 3), 57, 43],
        [ 'SEA', date(2021, 4, 2), 54, 39],
        [ 'SEA', date(2021, 4, 1), 56, 41]
        ]

        temps = self.spark.createDataFrame(data, schema)

        # Create a table on the cluster and then fill
        # the table with the DataFrame's contents.
        # If the table already exists from a previous run,
        # delete it first.
        self.spark.sql('USE default')
        self.spark.sql('DROP TABLE IF EXISTS demo_temps_table')
        temps.write.saveAsTable('demo_temps_table')

        # Query the table on the cluster, returning rows
        # where the airport code is not BLI and the date is later
        # than 2021-04-01. Group the results and order by high
        # temperature in descending order.
        df_temps = self.spark.sql("SELECT * FROM demo_temps_table " \
        "WHERE AirportCode != 'BLI' AND Date > '2021-04-01' " \
        "GROUP BY AirportCode, Date, TempHighF, TempLowF " \
        "ORDER BY TempHighF DESC")
        df_temps.show()

        # Results:
        #
        # +-----------+----------+---------+--------+
        # |AirportCode|      Date|TempHighF|TempLowF|
        # +-----------+----------+---------+--------+
        # |        PDX|2021-04-03|       64|      45|
        # |        PDX|2021-04-02|       61|      41|
        # |        SEA|2021-04-03|       57|      43|
        # |        SEA|2021-04-02|       54|      39|
        # +-----------+----------+---------+--------+

        # Clean up by deleting the table from the cluster.
        self.spark.sql('DROP TABLE demo_temps_table')

    def launch(self):
        self.logger.info("Launching sample DBX demo task")
        self._run_dbx_demo()
        self.logger.info("Dbx demo task finished!")

# if you're using python_wheel_task, you'll need the entrypoint function to be used in setup.py
def entrypoint():  # pragma: no cover
    task = DbxDemoTask()
    task.launch()

# if you're using spark_python_task, you'll need the __main__ block to start the code execution
if __name__ == '__main__':
    entrypoint()
