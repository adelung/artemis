from enum import StrEnum
from abc import ABC, abstractmethod
from typing import Callable


class StorageType(StrEnum):
    DIRECTORY = "directory"
    FILE = "file"
    INFLUXDB = "influxdb"


class Storage[T](ABC):

    @abstractmethod
    def add(self, item: T) -> str:
        pass

    @abstractmethod
    def getAll(self, transformer: Callable[str, T]) -> list[T]:
        pass

    @abstractmethod
    def get(self, id, transformer: Callable[str, T]) -> T:
        pass

    @abstractmethod
    def update(self, item: T) -> str:
        pass

    @abstractmethod
    def remove(self, id) -> bool:
        pass
