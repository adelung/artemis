# import json
# from influxdb import InfluxDBClient
# ... #definiera adress etc...
# ... #set sensorID, timestamp, histogram string, etc
# influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)

# json_body = [
#                     {
#                         "measurement": "artemis_sensor_measurement_001", # Need to specify the correct measurement name here
#                         "tags": {
#                             "sensorID": sensorID
#                         },
#                         "time": tstamp,
#                         "fields": {
#                             "counts_total": counts_total,
#                             "histogram_string": hist #save histogram as comma-separated string with brackets: "[1,3,4,...,0]"
#                         }
#                     }
#                 ]
# influxdb_client.write_points(json_body,time_precision='ms' )

from influxdb_client_3 import (
    InfluxDBClient3,
    Point,
    WriteOptions,
    InfluxDBError,
    write_client_options,
)
from typing import Final
from repository.storage import Storage
from models.serializable import Serializable
from models.sensor_data_point import SensorDataPoint


class BatchingCallback(object):

    def success(self, conf, data: str):
        print(f"Written batch: {conf}")

    def error(self, conf, data: str, exception: InfluxDBError):
        print(f"Cannot write batch: {conf}, data: {data} due: {exception}")

    def retry(self, conf, data: str, exception: InfluxDBError):
        print(f"Retryable error for batch: {conf}, data: {data} retry: {exception}")


callback = BatchingCallback()


class InfluxDBStorage(Storage[SensorDataPoint]):
    """
    InfluxDB storage that implements the Storage interface. Used for exporting the data to an InfluxDB instance.
    """

    HOST: Final = "http://10.20.30.37:8181"
    TOKEN: Final = (
        "apiv3__FdGnsr2t2vCJhL5HCFO6_lBfb4t_z_tLxg5eUzp2R5UhKl8KCTYZjs1BxtJ8mRse0K2FKgtHk59QsnjUwJw6Q"
    )
    BATCH_SIZE = 1000
    WRITE_OPTIONS = WriteOptions(
        batch_size=500,  # Number of points to batch before sending
        flush_interval=10_000,  # Flush every 10 seconds (in milliseconds)
        jitter_interval=2_000,  # Random delay to avoid thundering herd
        retry_interval=5_000,  # Retry after 5 seconds (in milliseconds)
        max_retries=5,  # Maximum number of retry attempts
        max_retry_delay=30_000,  # Maximum delay between retries (30 seconds)
        exponential_base=2,  # Exponential backoff base
    )
    clientOptions = write_client_options(
        success_callback=callback.success,
        error_callback=callback.error,
        retry_callback=callback.retry,
        write_options=WRITE_OPTIONS,
    )

    def __init__(self, sensorId):
        self.sensorId = sensorId
        self.client = InfluxDBClient3(
            token=InfluxDBStorage.TOKEN,
            host=InfluxDBStorage.HOST,
            database=sensorId,
            write_client_options=InfluxDBStorage.clientOptions,
        )

    def add(self, items: list[SensorDataPoint]) -> str:
        """
        Append items to InfluxDB.
        """
        self.client.write(items)
        # with self.client.write_api(write_options=InfluxDBStorage.WRITE_OPT) as api:
        #     api.write(bucket="my-bucket", record=items)
        # totalCount = len(items)
        # batchCount = int(totalCount / InfluxDBStorage.BATCH_SIZE)
        # for batch in range(batchCount):
        #     self.client.write(
        #         items[
        #             batch
        #             * InfluxDBStorage.BATCH_SIZE : (batch + 1)
        #             * InfluxDBStorage.BATCH_SIZE
        #         ],
        #         timeout=60,
        #     )

    def get(self, id) -> SensorDataPoint:
        pass

    def update(self, item: SensorDataPoint) -> str:
        pass

    def remove(self, id) -> bool:
        pass
