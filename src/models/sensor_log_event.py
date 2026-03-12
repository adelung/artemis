from dataclasses import dataclass
from datetime import datetime
from typing import Union, List, Self
from models.serializable import Serializable
import orjson


@dataclass
class SensorData:

    bn: str
    bt: int


@dataclass
class SensorDataNameOnly:

    bn: str


@dataclass
class SensorDataTimeOnly:

    bt: int


@dataclass
class SensorDataUnit:

    bu: str


@dataclass
class LoadData:

    n: str
    v: str


@dataclass
class LoadDataVector:

    n: str
    vs: str


@dataclass
class SensorLogEvent(Serializable["SensorLogEvent"]):

    receiveTimeStamp: datetime
    load: List[
        SensorData
        | SensorDataNameOnly
        | SensorDataTimeOnly
        | SensorDataUnit
        | LoadData
        | LoadDataVector
    ]

    @classmethod
    def deserializeLine(cls, text: str) -> Self:
        timestampString, loadString = text.split("] ", 1)
        receiveTimeStamp = datetime.strptime(
            timestampString.strip("[]"), "%Y-%m-%d %H:%M:%S"
        )
        loadString = loadString.strip(" \n")
        loadString = loadString.replace("'", '"')
        logEventJson = f'{{"receiveTimeStamp": {int(receiveTimeStamp.timestamp())}, "load": {loadString}}}'
        return cls.deserialize(logEventJson)
