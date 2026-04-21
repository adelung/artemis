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
        return SensorEvent(
            receiveTime,
            sensorTime,
            urn,
            eventType,
            load,
        )

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

    def isHistogramEvent(self) -> bool:
        return any(
            obj.get("n") == "histogram" or "histogram" in (obj.get("bn") or "")
            for obj in self.load
        )
