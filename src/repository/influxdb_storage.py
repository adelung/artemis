from influxdb_client_3 import InfluxDBClient3, Point
from typing import Final
from typing import Callable
from repository.storage import Storage, StorageType
from models.serializable import Serializable
from models.sensor_data_point import SensorDataPoint


class InfluxDBStorage(Storage[SensorDataPoint]):

    HOST: Final = "http://10.20.30.37:8181"
    TOKEN: Final = (
        "apiv3__FdGnsr2t2vCJhL5HCFO6_lBfb4t_z_tLxg5eUzp2R5UhKl8KCTYZjs1BxtJ8mRse0K2FKgtHk59QsnjUwJw6Q"
    )
    BATCH_SIZE = 1000

    def __init__(self, sensorId):
        self.sensorId = sensorId
        self.client = InfluxDBClient3(
            token=InfluxDBStorage.TOKEN, host=InfluxDBStorage.HOST, database=sensorId
        )

    def add(self, items: list[SensorDataPoint]) -> str:
        totalCount = len(items)
        batchCount = int(totalCount / InfluxDBStorage.BATCH_SIZE)
        for batch in range(batchCount):
            self.client.write(
                items[
                    batch
                    * InfluxDBStorage.BATCH_SIZE : (batch + 1)
                    * InfluxDBStorage.BATCH_SIZE
                ]
            )

    def getAll(
        self, transformer: Callable[str, SensorDataPoint]
    ) -> list[SensorDataPoint]:
        pass

    def get(self, id, transformer: Callable[str, SensorDataPoint]) -> SensorDataPoint:
        pass

    def update(self, item: SensorDataPoint) -> str:
        pass

    def remove(self, id) -> bool:
        pass


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
