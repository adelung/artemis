from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime
from typing import Union, List


@dataclass_json
@dataclass
class SensorData:

    bn: str
    bt: int


@dataclass_json
@dataclass
class SensorDataNameOnly:

    bn: str


@dataclass_json
@dataclass
class SensorDataTimeOnly:

    bt: int


@dataclass_json
@dataclass
class SensorDataUnit:

    bu: str


@dataclass_json
@dataclass
class LoadData:

    n: str
    v: str


@dataclass_json
@dataclass
class LoadDataVector:

    n: str
    vs: str


@dataclass_json
@dataclass
class SensorLogEvent:

    receiveTimeStamp: datetime
    load: List[
        SensorData
        | SensorDataNameOnly
        | SensorDataTimeOnly
        | SensorDataUnit
        | LoadData
        | LoadDataVector
    ]

    def decoder(obj):
        return SensorLogEvent(**obj)

    def deserializeLine(line: str):
        timestampString, loadString = line.split("] ", 1)
        receiveTimeStamp = datetime.strptime(
            timestampString.strip("[]"), "%Y-%m-%d %H:%M:%S"
        )
        loadString = loadString.strip(" \n")
        loadString = loadString.replace("'", '"')
        logEventJson = f'{{"receiveTimeStamp": {receiveTimeStamp.timestamp()}, "load": {loadString}}}'
        return SensorLogEvent.from_json(logEventJson)
