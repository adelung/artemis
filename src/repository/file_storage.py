from repository.storage import Storage
from models.serializable import Serializable
from pathlib import Path
from typing import Type


class FileStorage[T: Serializable](Storage[T]):
    """
    File storage that implements the Storage interface. Used for saving data in a file.
    """

    def __init__(self, path: str, cls: Type[T]):
        self.cls = cls
        self.filePath = Path(path)
        self.filePath.parent.mkdir(parents=True, exist_ok=True)
        if not self.filePath.exists():
            self.filePath.touch(exist_ok=True)

    def add(self, item: T) -> str:
        """
        Append item in the file after serializing in the nex line.
        """
        with self.filePath.open("a") as file:
            file.write(item.serialize() + "\n")

    def get(self, id) -> list[T]:
        """
        Get all data in the file after deserializing line by line.
        """
        with self.filePath.open("r") as file:
            items = [self.cls.deserialize(line) for line in file]
            return items

    def update(self, item: T) -> str:
        pass

    def remove(self, id) -> bool:
        """
        Remove current file.
        """
        if self.filePath.exists():
            self.filePath.unlink()
