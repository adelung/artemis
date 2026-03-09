from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Self
import orjson


T = TypeVar("T", bound="Serializable")


class Serializable(ABC, Generic[T]):

    def serialize(self) -> str:
        return orjson.dumps(self).decode("utf-8")

    @classmethod
    def deserialize(cls, text: str) -> T:
        jsonItem = orjson.loads(text)
        return cls(**jsonItem)
