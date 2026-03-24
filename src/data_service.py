from repository.directory_storage import DirectoryStorage
from repository.file_storage import FileStorage
from datetime import datetime
from influxdb_client_3 import Point
from repository.influxdb_storage import InfluxDBStorage
from models.sensor_log_event import SensorLogEvent
from models.sensor_event import SensorEvent, SensorEvents
from models.sensor_data_point import SensorDataPoint
from data_recovery import DataRecovery


class DataService:

    def getAllSensors(self, path: str) -> list[str]:
        directoryStorage = DirectoryStorage(path)
        return [
            directory.stem
            for directory in directoryStorage.listDirectories(None, sort=False)
        ]

    def collectDirectoryToFile(self, dataPath: str):
        directoryStorage = DirectoryStorage(dataPath)
        sensorsLogEvents = directoryStorage.getAll()
        for sensorId, logEvents in sensorsLogEvents:
            fileStorage = FileStorage[SensorEvent](
                f"{dataPath}/{sensorId}.txt", SensorEvent
            )
            for logEvent in logEvents:
                fileStorage.add(logEvent.toSensorEvent())

    def recoverData(self, dataPath: str, sensorId):
        fileStorageInput = FileStorage[SensorEvent](
            f"{dataPath}/{sensorId}.txt", SensorEvent
        )
        events = fileStorageInput.get(sensorId)

        sensorEvents = SensorEvents(sensorId, events)
        recoverer = DataRecovery(sensorEvents)
        sensorEvents = recoverer.recoverReceiveTimestamps()
        # sensorEvents = recoverer.recoverSensorTimestamps()

        fileStorageOutput = FileStorage[SensorEvent](
            f"{dataPath}/{sensorId}.fixed.txt", SensorEvent
        )
        for event in sensorEvents.events:
            fileStorageOutput.add(event)

    def exportToInfluxDB(self, dataPath: str, sensorId):
        fileStorage = FileStorage[SensorEvent](
            f"{dataPath}/{sensorId}.txt", SensorEvent
        )
        events = fileStorage.get(
            id=sensorId,
            transformer=lambda itemStr: SensorLogEvent.deserialize(itemStr),
        )
        dataPoints = [
            SensorDataPoint.fromSensorLogEvent(sensorId=sensorId, event=event)
            for event in events
            if any(obj.get("n") == "counts" for obj in event.load)
        ]
        points = [
            (
                Point("measurement")
                .tag("sensorID", sensorId)
                .field("counts_total", dataPoint.size)
                .field("histogram_string", dataPoint.histogram)
            )
            for dataPoint in dataPoints
        ]
        dbStorage = InfluxDBStorage(sensorId)
        dbStorage.add(points)

    def plotReceiveDelay(self, sensorId):
        print(f"=============================== {sensorId}")
        fileStorage = FileStorage[SensorEvent](
            f"data/{sensorId}.clean.txt", SensorEvent
        )
        events = fileStorage.get(sensorId)
        sensorEvents = SensorEvents(sensorId, events)
        quantile90 = sensorEvents.getReceiveDelayQuantile(0.95)
        sensorEvents.plotReceiveDelay(quantile90)

    def plotReceiveInterval(self, sensorId):
        print(f"=============================== {sensorId}")
        fileStorage = FileStorage[SensorEvent](
            f"data/{sensorId}.clean.txt", SensorEvent
        )
        events = fileStorage.get(sensorId)
        sensorEvents = (
            SensorEvents(sensorId, events).noneStatusEvents().histogramEvents()
        )
        # mean = sensorEvents.getReceiveIntervalMeanValueWithinQuantile(0.99)
        # print(f"Receive interval mean value: {mean}")
        sensorEvents.plotReceiveInterval(700)
