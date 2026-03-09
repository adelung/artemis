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

    def listDirectories(self, path: Path, sort=True) -> list[str]:
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

    def add(self, item: T) -> str:
        pass

    def getAll(self, transformer: Callable[str, T]) -> dict[str, list[T]]:
        sensorsFiles = {}
        sensorsEvents = {}
        sensorDirectories = self.listDirectories(None, sort=False)

        for sensorPath in sensorDirectories:
            sensorId = sensorPath.stem
            sensorsFiles[sensorId] = list()
            sensorsEvents[sensorPath.stem] = list()
            for year in self.listDirectories(sensorPath):
                for month in self.listDirectories(year):
                    sensorsFiles[sensorId].extend(self.listFiles(month))

        for sensorId, sensorFiles in sensorsFiles.items():
            for filePath in sensorFiles:
                print(filePath)
                with filePath.open("r") as file:
                    items = [transformer(line) for line in file]
                    sensorsEvents[sensorId].extend(items)

        return sensorsEvents

    def get(self, id, transformer: Callable[str, T]) -> T:
        pass

    def update(self, item: T) -> str:
        pass

    def remove(self, id) -> bool:
        pass
