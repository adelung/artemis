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

    def __init__(self, dataPath, outPath):
        self.dataPath = dataPath
        self.outPath = outPath
        self.directoryStorage = DirectoryStorage(dataPath)

    def getAllSensors(self) -> list[str]:
        return [
            directory.stem
            for directory in self.directoryStorage.listDirectories(None, sort=False)
        ]

    def collectDirectoryToFile(self, sensorId: str, iso: bool):
        logEvents = self.directoryStorage.get(sensorId)
        events = [event.toSensorEvent() for event in logEvents]
        sensorEvents = SensorEvents(sensorId, events)
        recoverer = DataRecovery(sensorEvents)
        sensorEvents = recoverer.recoverReceiveTime().noneStatusEvents()
        outputFilePath = f"{self.outPath}/{sensorId}.noneStatus.txt"

        if iso:
            sensorEvents = sensorEvents.toIso()
            outputFilePath = f"{self.outPath}/{sensorId}.iso.txt"

        fileStorage = FileStorage[SensorEvent](outputFilePath, SensorEvent)
        for event in sensorEvents.events:
            fileStorage.add(event)

    def recoverData(self, sensorId):
        fileStorageInput = FileStorage[SensorEvent](
            f"{self.outPath}/{sensorId}.txt", SensorEvent
        )
        events = fileStorageInput.get(sensorId)
        sensorEvents = SensorEvents(sensorId, events).noneStatusEvents()
        if sensorEvents.empty():
            print(f"Sensor {sensorEvents.sensorId} missing events")
        else:
            recoverer = DataRecovery(sensorEvents)
            sensorEvents = recoverer.recoverSensorTime()
            fileStorageOutput = FileStorage[SensorEvent](
                f"{self.outPath}/{sensorId}.recovered.txt", SensorEvent
            )
            for event in sensorEvents.events:
                fileStorageOutput.add(event)

    def exportToInfluxDB(self, sensorId):
        fileStorage = FileStorage[SensorEvent](
            f"{self.outPath}/{sensorId}.txt", SensorEvent
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
        fileStorage = FileStorage[SensorEvent](f"data/{sensorId}.txt", SensorEvent)
        events = fileStorage.get(sensorId)
        sensorEvents = SensorEvents(sensorId, events).histogramEvents()
        if sensorEvents.empty():
            print(f"Sensor {sensorEvents.sensorId} missing events")
        else:
            _, max, _ = sensorEvents.getReceiveDelayRange(0.95)
            sensorEvents.plotReceiveDelay(max)

    def plotReceiveInterval(self, sensorId):
        print(f"=============================== {sensorId}")
        fileStorage = FileStorage[SensorEvent](f"data/{sensorId}.txt", SensorEvent)
        events = fileStorage.get(sensorId)
        sensorEvents = SensorEvents(
            sensorId, events
        ).noneStatusEvents()  # .histogramEvents()
        if sensorEvents.empty():
            print(f"Sensor {sensorEvents.sensorId} missing events")
        else:
            _, max, _ = sensorEvents.getReceiveIntervalRange(0.95)
            sensorEvents.plotReceiveInterval(max)
