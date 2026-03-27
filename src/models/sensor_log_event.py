# Data class for the sensor events as in the directory database.

from dataclasses import dataclass
from zoneinfo import ZoneInfo
from datetime import datetime, timezone
from typing import Self
from models.serializable import Serializable
from models.sensor_event import (
    EventType,
    SensorEvent,
    SensorHistogram,
    SensorPHT,
    SensorAccelerometer,
    SensorGyroscope,
    SensorMagnet,
    SensorEC,
    SensorP,
    SensorMic,
    SensorGatewayStatus,
)
from urnparse import URN8141, InvalidURNFormatError, NSSString, NSIdentifier
import numpy as np


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
class SensorDataUnitOnly:

    bu: str


@dataclass
class LoadData:

    n: str
    v: str


@dataclass
class LoadDataWithUnit:

    n: str
    u: str
    v: str


@dataclass
class LoadDataVector:

    n: str
    vs: str


@dataclass
class SensorLogEvent(Serializable["SensorLogEvent"]):

    receiveTimestamp: int
    load: list[
        SensorData
        | SensorDataNameOnly
        | SensorDataTimeOnly
        | SensorDataUnitOnly
        | LoadData
        | LoadDataWithUnit
        | LoadDataVector
    ]

    @classmethod
    def deserialize(cls, text: str) -> Self:
        receiveTimeString, loadString = text.split("] ", 1)
        receiveTime = datetime.strptime(
            receiveTimeString.strip("[]"), "%Y-%m-%d %H:%M:%S"
        )
        loadString = loadString.strip(" \n")
        loadString = loadString.replace("'", '"')
        receiveTime = int(receiveTime.timestamp())
        logEventJson = f'{{"receiveTimestamp": "{receiveTime}", "load": {loadString}}}'
        return super().deserialize(logEventJson)

    def toSensorEvent(self) -> SensorEvent:
        urn = self.getOriginalURN()
        sensorTime = self.getSensorTimestamp()
        receiveTime = int(self.receiveTimestamp)
        eventType = self.getEventType()
        load = self.getLoad(eventType)
        # receiveTimestamp = datetime.fromisoformat(self.receiveTimestamp)
        # receiveTimestamp = datetime.fromtimestamp(
        #     int(self.receiveTimestamp), tz=timezone.utc
        # )
        return SensorEvent(
            receiveTime,
            sensorTime,
            urn,
            eventType,
            load,
        )

    # # Old
    # {"receiveTimestamp":1707922771,"load":[{"bn":"urn:dev:10000000aa212a2b:sensor","bt":1707922771583},{"n":"histogram","vs":"[0, 38, 56, 35, 22, 16, 1, 4, 8, 2, 4, 1, 7, 3, 2, 3, 1, 3, 3, 2, 3, 4, 4, 17, 7, 4, 3, 3, 2, 1, 1, 4, 8, 3, 6, 9, 12, 5, 6, 6, 6, 2, 6, 9, 8, 7, 6, 5, 10, 10, 5, 5, 7, 4, 4, 6, 11, 20, 10, 13, 15, 7, 7, 9, 11, 9, 10, 15, 10, 12, 6, 9, 12, 8, 12, 9, 13, 13, 12, 7, 6, 5, 18, 12, 18, 14, 10, 6, 8, 9, 12, 7, 9, 7, 12, 8, 10, 9, 12, 10, 11, 10, 15, 9, 10, 8, 8, 18, 13, 10, 16, 10, 9, 12, 10, 10, 9, 9, 8, 9, 13, 8, 14, 11, 8, 6, 9, 9, 8, 10, 10, 9, 11, 5, 6, 7, 8, 8, 9, 12, 5, 13, 7, 5, 8, 8, 7, 10, 5, 8, 8, 8, 14, 3, 6, 4, 8, 18, 9, 8, 9, 2, 5, 10, 5, 4, 6, 8, 4, 5, 6, 6, 6, 9, 5, 3, 8, 3, 4, 2, 4, 1, 3, 1, 3, 4, 4, 3, 7, 4, 1, 4, 2, 6, 4, 3, 0, 9, 4, 4, 3, 2, 3, 1, 5, 6, 5, 2, 2, 7, 5, 4, 2, 3, 6, 5, 3, 10, 8, 5, 6, 3, 10, 2, 1, 4, 4, 1, 4, 0, 0, 4, 3, 2, 2, 5, 5, 0, 2, 2, 1, 0, 2, 4, 3, 3, 1, 2, 3, 2, 1, 4, 4, 1, 3, 4, 1, 2, 1, 4, 6, 4, 2, 2, 0, 2, 0, 3, 3, 5, 3, 2, 0, 4, 0, 1, 2, 2, 1, 2, 3, 0, 0, 0, 1, 2, 2, 3, 2, 2, 1, 3, 3, 1, 1, 3, 1, 0, 0, 0, 1, 0, 2, 0, 0, 1, 1, 1, 0, 5, 0, 0, 1, 2, 1, 0, 2, 1, 0, 1, 1, 0, 0, 0, 0, 1, 3, 0, 1, 1, 0, 0, 1, 1, 3, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 3, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 0, 0, 0, 0, 92]"}]}
    # {"receiveTimestamp":1707922801,"load":[{"bn":"urn:dev:10000000aa212a2b:gw:sensor","bt":1707922801753},{"n":"write_ok","v":18},{"n":"read_ok","v":18},{"n":"read_partial","v":0},{"n":"read_timeout","v":0},{"n":"read_overflow","v":0}]}

    # # New
    # {"receiveTimestamp":1737907661,"load":[{"bn":"urn:dev:10000000aa212a2b:gw:stats","bt":1737907661538},{"n":"malloc","vs":"41/45 48152/64576"},{"n":"circbuf","vs":"0/1/1024"},{"n":"up_since","v":1737548225723},{"n":"sys_uptime","v":354408},{"n":"load","vs":"0.00 0.00 0.00 2/242 28085"}]}
    # {"receiveTimestamp":1737907742,"load":[{"bn":"urn:dev:10000000aa212a2b:sensor:histogram"},{"n":"size","v":500},{"n":"counts","vs":"[0,167,172,158,135,51,3,23,27,9,9,15,10,6,4,5,12,11,9,3,8,10,33,31,24,18,5,4,3,2,4,6,28,30,26,21,23,19,18,17,22,17,23,26,29,30,21,33,37,38,32,32,18,20,17,25,27,36,32,25,40,45,35,36,36,25,27,42,43,29,36,44,36,36,42,37,43,46,34,27,21,34,32,29,34,48,50,35,47,37,43,26,31,21,43,42,30,46,40,42,38,48,41,52,43,26,33,42,47,31,33,35,37,38,28,37,36,41,33,36,34,36,35,40,29,31,25,37,31,34,43,28,31,23,32,34,32,17,33,31,23,33,28,28,19,30,21,27,24,26,24,23,20,22,12,28,35,24,16,24,17,22,25,17,21,18,20,15,17,16,18,22,17,21,16,17,21,18,23,21,25,13,8,9,17,12,9,9,8,16,15,10,8,14,17,14,16,6,13,6,9,12,13,11,10,9,11,10,8,9,8,12,13,8,14,6,7,7,8,8,9,10,8,6,12,11,5,13,10,10,12,8,12,9,7,9,11,8,7,3,6,10,10,5,3,8,6,8,6,6,7,5,6,1,3,13,6,10,8,7,3,4,9,7,10,4,6,5,1,13,3,6,4,4,4,4,7,4,4,4,4,2,3,7,5,3,5,5,6,4,6,2,2,6,6,5,2,2,3,3,2,6,1,2,5,4,8,3,4,5,2,2,2,5,3,3,7,5,7,5,5,1,2,2,4,1,2,4,3,3,2,3,1,2,1,2,0,1,1,0,1,1,1,1,2,0,1,1,1,2,1,1,0,1,1,0,0,0,2,1,1,0,3,1,1,2,0,0,2,0,0,2,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,18]"}]}
    # {"receiveTimestamp":1737907742,"load":[{"bn":"urn:dev:10000000aa212a2b:sensor:pht"},{"bt":1737902259},{"n":"p","u":"hPa","v":998.004},{"n":"h","u":"%","v":22.158},{"n":"t","u":"C","v":26.25},{"n":"a","u":"m","v":127.712}]}
    # {"receiveTimestamp":1737907742,"load":[{"bn":"urn:dev:10000000aa212a2b:sensor:acc"},{"bt":1737902259},{"n":"x","u":"m/s2","v":9.824},{"n":"y","u":"m/s2","v":0.179},{"n":"z","u":"m/s2","v":-1.169},{"n":"t","u":"C","v":26.488}]}
    # {"receiveTimestamp":1737907743,"load":[{"bn":"urn:dev:10000000aa212a2b:sensor:gyro"},{"bt":1737902259},{"n":"x","u":"rad/s","v":0.002},{"n":"y","u":"mrad/s","v":-0.012},{"n":"z","u":"mrad/s","v":-0.002}]}
    # {"receiveTimestamp":1737907743,"load":[{"bn":"urn:dev:10000000aa212a2b:sensor:mag"},{"bt":1737902260},{"n":"x","u":"uT","v":-46.331},{"n":"y","u":"uT","v":-43.087},{"n":"z","u":"uT","v":-20.286}]}
    # {"receiveTimestamp":1737907743,"load":[{"bn":"urn:dev:10000000aa212a2b:sensor"},{"bt":1737902266},{"n":"ec","v":780.0}]}
    # {"receiveTimestamp":1737907743,"load":[{"bn":"urn:dev:10000000aa212a2b:sensor"},{"bt":1737902266},{"n":"p","v":748.0}]}
    # {"receiveTimestamp":1737907743,"load":[{"bn":"urn:dev:10000000aa212a2b:sensor"},{"bt":1737902266},{"n":"mic","v":839.0}]}

    def getLoad(self, eventType: EventType):
        match eventType:
            case EventType.HISTOGRAM:
                histogram = self.getHistogram()
                return SensorHistogram(
                    len(histogram),
                    histogram,
                )
            case EventType.PHT:
                return SensorPHT(
                    self.get("p"),
                    self.get("h"),
                    self.get("t"),
                    self.get("a"),
                )
            case EventType.acc:
                return SensorAccelerometer(
                    self.get("x"),
                    self.get("y"),
                    self.get("z"),
                    self.get("t"),
                )
            case EventType.GYRO:
                return SensorGyroscope(
                    self.get("x"),
                    self.get("y"),
                    self.get("z"),
                )
            case EventType.MAG:
                return SensorMagnet(
                    self.get("x"),
                    self.get("y"),
                    self.get("z"),
                )
            case EventType.EC:
                return SensorEC(
                    self.get("ec"),
                )
            case EventType.P:
                return SensorP(
                    self.get("p"),
                )
            case EventType.MIC:
                return SensorMic(
                    self.get("mic"),
                )
            case _:
                return SensorGatewayStatus(self.get("bn"))

    def getOriginalURN(self) -> str:
        return next((obj.get("bn") for obj in self.load if obj.get("bn")), None)

    def getURN(self) -> URN8141:
        urnString = self.getOriginalURN()
        try:
            if self.isHistogramEvent() and "histogram" not in urnString:
                return URN8141.from_string(f"{urnString}:histogram")
            else:
                return URN8141.from_string(urnString)
        except InvalidURNFormatError:
            nid = NSIdentifier("dev")
            nss = NSSString(f"sensorId:{urnString}", encoded=True)
            return URN8141(nid=nid, nss=nss)

    def getEventType(self) -> EventType:
        urn = self.getURN()
        urnParts = urn.specific_string.parts
        device = next(iter(urnParts[1:2]), None)
        eventTypeString = next(iter(urnParts[2:3]), None)
        if device != "gw" and eventTypeString:
            return (
                EventType(eventTypeString)
                if eventTypeString
                else next(EventType(obj.get("n")) for obj in self.load if obj.get("n"))
            )
        elif self.isHistogramEvent():
            return EventType.HISTOGRAM

    def isHistogramEvent(self) -> bool:
        return any(
            obj.get("n") == "histogram" or "histogram" in (obj.get("bn") or "")
            for obj in self.load
        )

    def getSensorTimestamp(self) -> datetime:
        sensorTimestamp = next(
            (obj.get("bt") for obj in self.load if obj.get("bt") != None), None
        )
        if sensorTimestamp:
            return (
                sensorTimestamp // 1000
                if sensorTimestamp > 9999999999
                else sensorTimestamp
            )

    def getHistogram(self) -> list[int]:
        histogramString = next(
            (
                obj.get("vs")
                for obj in self.load
                if obj.get("n") == "histogram" or obj.get("n") == "counts"
            ),
            None,
        )
        if histogramString:
            return np.fromstring(histogramString[1:-1], dtype=int, sep=", ").tolist()

    def get(self, item) -> list[int]:
        itemString = next(
            (obj.get("v") for obj in self.load if obj.get("n") == item),
            None,
        )
        if itemString:
            return float(itemString)
