# Data are stored in a file per sensor with all the data ordered by time.

from enum import StrEnum
from typing import Callable
from repository.storage import Storage, StorageType
from models.serializable import Serializable
from pathlib import Path
import orjson


class FileStorage[T: Serializable](Storage[T]):

    def __init__(self, path: str):
        self.filePath = Path(path)
        self.filePath.parent.mkdir(parents=True, exist_ok=True)
        self.filePath.touch(exist_ok=True)

    def add(self, item: T) -> str:
        with self.filePath.open("a") as file:
            file.write(item.serialize() + "\n")

    def getAll(self, transformer: Callable[str, T]) -> list[T]:
        pass

    def get(self, id, transformer: Callable[str, T]) -> T:
        with self.filePath.open("r") as file:
            items = [transformer(line) for line in file]
            return items

    def update(self, item: T) -> str:
        pass

    def remove(self, id) -> bool:
        pass
