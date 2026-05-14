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
    """
    DataService class is used to help organize data access, plot and storage.
    """

    def __init__(self, dataPath):
        self.dataPath = dataPath
        self.directoryStorage = DirectoryStorage(dataPath)

    def getAllSensors(self) -> list[str]:
        """
        List available sensor ids in the data directory.
        """
        return [
            directory.stem
            for directory in self.directoryStorage.listDirectories(None, sort=False)
        ]

    def collectDirectoryToFile(self, sensorId: str, iso: bool):
        """
        Collect the sensor data to a single file with the sensorId as the name.
        """
        logEvents = self.directoryStorage.get(sensorId)
        events = [event.toSensorEvent() for event in logEvents]
        sensorEvents = SensorEvents(sensorId, events)
        recoverer = DataRecovery(sensorEvents)
        sensorEvents = recoverer.recoverReceiveTime().noneStatusEvents()
        outputFilePath = f"{self.dataPath}/{sensorId}.txt"

        if iso:
            sensorEvents = sensorEvents.toIso()
            outputFilePath = f"{self.dataPath}/{sensorId}.iso.txt"

        fileStorage = FileStorage[SensorEvent](outputFilePath, SensorEvent)
        fileStorage.remove(sensorId)
        for event in sensorEvents.events:
            fileStorage.add(event)

    def recoverData(self, sensorId: str):
        """
        Run data recovery process for sensorId.
        """
        fileStorageInput = FileStorage[SensorEvent](
            f"{self.dataPath}/{sensorId}.txt", SensorEvent
        )
        events = fileStorageInput.get(sensorId)
        sensorEvents = SensorEvents(sensorId, events).noneStatusEvents()
        if sensorEvents.empty():
            print(f"Sensor {sensorEvents.sensorId} missing events")
        else:
            recoverer = DataRecovery(sensorEvents)
            sensorEvents = recoverer.recoverSensorTime()
            sensorEvents = recoverer.flattenHistogram()
            fileStorageOutput = FileStorage[SensorEvent](
                f"{self.dataPath}/{sensorId}.recovered.txt", SensorEvent
            )
            fileStorageOutput.remove(sensorId)
            for event in sensorEvents.events:
                fileStorageOutput.add(event)

    def exportToInfluxDB(self, sensorId: str):
        """
        Export the recovered data to InfluxDB for sensorId.
        """
        fileStorage = FileStorage[SensorEvent](
            f"{self.dataPath}/{sensorId}.recovered.txt", SensorEvent
        )
        events = fileStorage.get(
            id=sensorId,
            transformer=lambda itemStr: SensorLogEvent.deserialize(itemStr),
        )
        dataPoints = [
            SensorDataPoint.fromSensorEvent(sensorId=sensorId, event=event)
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

    def plotSensorCaptures(self, sensorId: str, recovered: bool):
        """
        Plot sensor timestamps before/after recovering timestamps.
        """
        fileStorage = FileStorage[SensorEvent](
            f"data/{sensorId}{".recovered" if recovered else "" }.txt", SensorEvent
        )
        events = fileStorage.get(sensorId)
        sensorEvents = (
            SensorEvents(sensorId, events).noneStatusEvents().noneHistogramEvents()
        )
        if sensorEvents.empty():
            print(f"Sensor {sensorEvents.sensorId} missing events")
        else:
            sensorEvents.plotSensorCaptures()

    def plotSensorInterval(self, sensorId: str, recovered: bool):
        """
        Plot interval between consecutive receive timestamps.
        """
        fileStorage = FileStorage[SensorEvent](
            f"data/{sensorId}{".recovered" if recovered else "" }.txt", SensorEvent
        )
        events = fileStorage.get(sensorId)
        sensorEvents = SensorEvents(
            sensorId, events
        ).noneStatusEvents()  # .histogramEvents()
        if sensorEvents.empty():
            print(f"Sensor {sensorEvents.sensorId} missing events")
        else:
            sensorEvents.plotSensorTimeInterval()

    def plotReceiveDelay(self, sensorId: str, recovered: bool):
        """
        Plot the delay between sensor timestamp and receive timestamp before/after recovering timestamps.
        """
        fileStorage = FileStorage[SensorEvent](
            f"data/{sensorId}{".recovered" if recovered else "" }.txt", SensorEvent
        )
        events = fileStorage.get(sensorId)
        sensorEvents = SensorEvents(sensorId, events)
        if sensorEvents.empty():
            print(f"Sensor {sensorEvents.sensorId} missing events")
        else:
            _, max, _ = sensorEvents.getReceiveDelayRange(0.95)
            sensorEvents.plotReceiveDelay(max)

    def plotReceiveInterval(self, sensorId: str):
        """
        Plot interval between consecutive receive timestamps.
        """
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

    def plotRadon(self, sensorId: str, recovered: bool):
        """
        Plot radon histogram data before/after recovering timestamps.
        """
        fileStorage = FileStorage[SensorEvent](
            f"data/{sensorId}{".recovered" if recovered else "" }.txt", SensorEvent
        )
        events = fileStorage.get(sensorId)
        sensorEvents = SensorEvents(sensorId, events)
        sensorEvents.plotRadonHistogram()
