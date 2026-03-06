from repository.directory_storage import DirectoryStorage
from repository.file_storage import FileStorage
from models.sensor_log_event import SensorLogEvent, SensorData, SensorDataTimeOnly
import matplotlib.pyplot as plt
import numpy as np
import mplcursors


class DataService:

    def migrateDirectoryToFile(self, path: str):
        directoryStorage = DirectoryStorage[SensorLogEvent](path)
        sensorEvents = directoryStorage.getAll(
            transformer=lambda itemStr: SensorLogEvent.deserializeLine(itemStr),
        )
        for sensor, events in sensorEvents.items():
            fileStorage = FileStorage(f"{path}/{sensor}.txt")
            for event in events:
                fileStorage.add(event)

    def getAllSensors(self, path: str):
        directoryStorage = DirectoryStorage[SensorLogEvent](path)
        return [file.stem for file in directoryStorage.listFiles(None)]

    def plotReceiveTimeVsSensorTime(self, sensorId):
        fileStorage = FileStorage[SensorLogEvent](f"data/{sensorId}.txt")
        events = fileStorage.get(
            id=sensorId,
            transformer=lambda itemStr: SensorLogEvent.from_json(itemStr),
        )
        timeDistribution = []
        for event in events:
            load = event.load
            for obj in load:
                receivedTimeStamp = event.receiveTimeStamp.timestamp()
                receivedTimeStamp = (
                    receivedTimeStamp * 1000
                    if receivedTimeStamp <= 99999999991738355482
                    else receivedTimeStamp
                )
                if isinstance(obj, SensorData) or isinstance(obj, SensorDataTimeOnly):
                    sensorTimeStamp = obj.bt
                    sensorTimeStamp = (
                        sensorTimeStamp * 1000
                        if sensorTimeStamp <= 9999999999
                        else sensorTimeStamp
                    )
                    delay = receivedTimeStamp - sensorTimeStamp
                    delay /= 1000
                    timeDistribution.append(delay)

        # plt.hist(timeDistribution, bins="auto", edgecolor="grey", alpha=0.7)
        x = [i for i in range(len(timeDistribution))]

        fig, ax = plt.subplots()

        ax.plot(x, timeDistribution, "-")
        plt.title("Distribution Plot (Histogram)")
        plt.xlabel("Event")
        plt.ylabel("Delay")
        plt.grid(True, alpha=0.3)

        # Add interactive cursor
        cursor = mplcursors.cursor(ax, hover=True)
        cursor.connect(
            "add",
            lambda sel: sel.annotation.set_text(
                f"x={sel.target[0]:.2f}, y={sel.target[1]:.2f}"
            ),
        )

        plt.show()
