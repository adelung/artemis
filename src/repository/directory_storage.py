from repository.storage import Storage
from models.sensor_log_event import SensorLogEvent
from typing import Callable
from pathlib import Path


class DirectoryStorage(Storage[SensorLogEvent]):
    """
    Directory storage that implements the Storage interface. Used for accessing the existing data before recovery.
    The structure of the directory is as follows:
    The root directory containing a directory per sensor. Each sensor directory contains a directory
    per year which includes a directory per month which includes a file per day.
    """

    def __init__(self, path: str):
        self.rootPath = Path(path)

    def listDirectories(self, path: Path, sort=True) -> list[str]:
        """
        List all directories inside path sorting if sort=True.
        """
        dirPath = path if path else self.rootPath
        if dirPath.exists():
            dirlist = [item for item in dirPath.iterdir() if item.is_dir()]
            return (
                sorted(dirlist, key=lambda dirItem: int(dirItem.stem))
                if sort
                else dirlist
            )
        else:
            return []

    def listFiles(self, path: Path | None, sort=True) -> list[str]:
        """
        List all files inside path sorting if sort=True.
        """
        dirPath = path if path else self.rootPath
        if dirPath.exists():
            fileList = [item for item in dirPath.iterdir() if item.is_file()]
            return (
                sorted(fileList, key=lambda fileItem: int(fileItem.stem))
                if sort
                else fileList
            )
        else:
            return []

    def add(self, event: SensorLogEvent) -> str:
        pass

    def get(self, id) -> list[SensorLogEvent]:
        """
        Get the list of all events for the sensor with id.
        """
        sensorFiles = []
        sensorEvents = []

        for year in self.listDirectories(self.rootPath / id):
            for month in self.listDirectories(year):
                sensorFiles.extend(self.listFiles(month))

        for filePath in sensorFiles:
            print(filePath)
            with filePath.open("r") as file:
                fileEvents = [SensorLogEvent.deserialize(line) for line in file]
                sensorEvents.extend(fileEvents)

        return sensorEvents

    def update(self, event: SensorLogEvent) -> str:
        pass

    def remove(self, id) -> bool:
        pass
