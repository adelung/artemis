# The structure of the directory is as follows:
# The root directory containing a directory per sensor. Each sensor directory contains a directory
# per year which includes a directory per month which includes a file per day.

from repository.storage import Storage
from typing import Callable
from pathlib import Path
import os


class DirectoryStorage[T](Storage[T]):

    def __init__(self, path: str):
        self.rootPath = Path(path)

    def listDirectories(self, path: Path) -> list[str]:
        dirPath = path if path else self.rootPath
        if dirPath.exists():
            return [item for item in dirPath.iterdir() if item.is_dir()]
        else:
            return []

    def listFiles(self, path: Path | None) -> list[str]:
        dirPath = path if path else self.rootPath
        if dirPath.exists():
            return [item for item in dirPath.iterdir() if item.is_file()]
        else:
            return []

    def add(self, item: T) -> str:
        pass

    def getAll(self, transformer: Callable[str, T]) -> dict[str, list[T]]:
        sensorsEvents = {}
        sensors = self.listDirectories(None)
        days = list()

        for sensor in sensors:
            sensorsEvents[sensor.stem] = []
            for year in self.listDirectories(sensor):
                for month in self.listDirectories(year):
                    days.extend(self.listFiles(month))

        days = sorted(days, key=lambda day: int(day.stem))

        for filePath in days:
            sensor = filePath.parts[1]
            print(filePath)
            with filePath.open("r") as file:
                items = [transformer(line) for line in file]
                sensorsEvents[sensor].extend(items)

        return sensorsEvents

    def get(self, id, transformer: Callable[str, T]) -> T:
        pass

    def update(self, item: T) -> str:
        pass

    def remove(self, id) -> bool:
        pass
