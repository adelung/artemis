from abc import ABC, abstractmethod


class Storage[T](ABC):
    """
    An abstract class that represent a storage abstraction.
    The implementation follows CRUD abstraction but implements its own data access layer.
    """

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
