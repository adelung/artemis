from abc import ABC, abstractmethod


class Storage[T](ABC):

    @abstractmethod
    def add(self, item: T) -> str:
        pass

    @abstractmethod
    def get(self, id) -> list[T]:
        pass

    @abstractmethod
    def update(self, item: T) -> str:
        pass

    @abstractmethod
    def remove(self, id) -> bool:
        pass
