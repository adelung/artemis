from repository.directory_storage import DirectoryStorage
from influxdb_client_3 import Point
from repository.file_storage import FileStorage
from repository.influxdb_storage import InfluxDBStorage
from models.sensor_log_event import SensorLogEvent, SensorData, SensorDataTimeOnly
from models.sensor_data_point import SensorDataPoint
import matplotlib.pyplot as plt
import numpy as np
import mplcursors


class DataService:

    def migrateDirectoryToFile(self, dataPath: str):
        directoryStorage = DirectoryStorage[SensorLogEvent](dataPath)
        sensorEvents = directoryStorage.getAll(
            transformer=lambda itemStr: SensorLogEvent.deserializeLine(itemStr),
        )
        for sensor, events in sensorEvents.items():
            fileStorage = FileStorage(f"{dataPath}/{sensor}.txt")
            for event in events:
                fileStorage.add(event)

    def getAllSensors(self, path: str):
        directoryStorage = DirectoryStorage[SensorLogEvent](path)
        return [file.stem for file in directoryStorage.listFiles(None, sort=False)]

    def migrateDataToInfluxDB(self, dataPath: str, sensorId):
        fileStorage = FileStorage(f"{dataPath}/{sensorId}.txt")
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

    def addCursor(self, ax):
        cursor = mplcursors.cursor(ax, hover=True)
        cursor.connect(
            "add",
            lambda sel: sel.annotation.set_text(
                f"x={sel.target[0]:.2f}, y={sel.target[1]:.2f}"
            ),
        )

    def isHistogramEvent(self, event) -> list[SensorLogEvent]:
        return any(
            obj.get("n") == "histogram" or "histogram" in (obj.get("bn") or "")
            for obj in event.load
        )

    def plotReceiveDelay(self, sensorId):
        fileStorage = FileStorage[SensorLogEvent](f"data/{sensorId}.txt")
        events = fileStorage.get(
            id=sensorId,
            transformer=lambda itemStr: SensorLogEvent.deserialize(itemStr),
        )
        timeDistribution = []
        for event in events:
            load = event.load
            if self.isHistogramEvent(event):
                sensorTimeStamp = next(
                    (obj.get("bt") for obj in load if obj.get("bt") != None), None
                )
                if sensorTimeStamp:
                    sensorTimeStamp = (
                        sensorTimeStamp * 1000
                        if sensorTimeStamp <= 9999999999
                        else sensorTimeStamp
                    )
                    receivedTimeStamp = event.receiveTimeStamp
                    receivedTimeStamp = (
                        receivedTimeStamp * 1000
                        if receivedTimeStamp <= 9999999999
                        else receivedTimeStamp
                    )
                    delay = receivedTimeStamp - sensorTimeStamp
                    timeDistribution.append(delay)

        fig, ax = plt.subplots()
        ax.hist(timeDistribution, bins="auto", edgecolor="grey", alpha=0.7)
        plt.title(
            "Delay Histogram (Negative delay < 1000ms due to receive time is captured with second accuracy)"
        )
        plt.xlabel("Delay [ms]")
        plt.ylabel("Count")
        plt.grid(True, alpha=0.3)
        self.addCursor(ax)
        plt.show()

    def plotTimeGap(self, sensorId):
        fileStorage = FileStorage[SensorLogEvent](f"data/{sensorId}.txt")
        events = fileStorage.get(
            id=sensorId,
            transformer=lambda itemStr: SensorLogEvent.deserialize(itemStr),
        )
        events = [event for event in events if self.isHistogramEvent(event)]
        timeDistribution = []
        for index in range(len(events) - 1):
            currentEvent = events[index]
            currentEventTimestamp = currentEvent.receiveTimeStamp

            nextEvent = events[index + 1]
            nextEventTimestamp = nextEvent.receiveTimeStamp

            delay = nextEventTimestamp - currentEventTimestamp
            # if delay > 20 * 60:
            #     print(currentEventTimestamp)
            timeDistribution.append(delay)

        fig, ax = plt.subplots()
        x = range(len(timeDistribution))
        ax.plot(x, timeDistribution, "bo-", label="Squared values")
        plt.title("Delay consecutive timestamps")
        plt.xlabel("Event [#]")
        plt.ylabel("Delay [s]")
        plt.grid(True, alpha=0.3)
        self.addCursor(ax)
        plt.show()

    def migrateToInfluxDB(self, sensorId):
        pass
