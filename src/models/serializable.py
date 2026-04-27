from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Self
import orjson


T = TypeVar("T", bound="Serializable")


class Serializable(ABC, Generic[T]):
    """
    An abstract class that represent any serializable data class. It uses orjson to serialize/deserialize from to json.
    """

    def serialize(self) -> str:
        """
        Serialize this instance to json.
        """
        return orjson.dumps(self).decode("utf-8")

    @classmethod
    def deserialize(cls, text: str) -> T:
        """
        Deserialize this the text from json to cls.
        """
        jsonItem = orjson.loads(text)
        return cls(**jsonItem)
