# Data are stored in a file per sensor with all the data ordered by time.

from repository.storage import Storage
from models.serializable import Serializable
from pathlib import Path
from typing import Type


class FileStorage[T: Serializable](Storage[T]):

    def __init__(self, path: str, cls: Type[T]):
        self.cls = cls
        self.filePath = Path(path)
        self.filePath.parent.mkdir(parents=True, exist_ok=True)
        self.filePath.touch(exist_ok=True)

    def add(self, item: T) -> str:
        with self.filePath.open("a") as file:
            file.write(item.serialize() + "\n")

    def get(self, id) -> T:
        with self.filePath.open("r") as file:
            items = [self.cls.deserialize(line) for line in file]
            return items

    def update(self, item: T) -> str:
        pass

    def remove(self, id) -> bool:
        pass
