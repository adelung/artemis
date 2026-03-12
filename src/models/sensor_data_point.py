from dataclasses import dataclass
from datetime import datetime
from typing import Union, Self
from models.serializable import Serializable
from models.sensor_log_event import SensorLogEvent


@dataclass
class SensorDataPoint(Serializable["SensorDataPoint"]):

    time: datetime
    sensorId: str
    size: int
    histogram: str

    def fromSensorLogEvent(sensorId: str, event: SensorLogEvent) -> Self:
        load = event.load
        size = None
        histogram = None
        for obj in load:
            if obj.get("n") == "size":
                size = obj.get("v")
            if obj.get("n") == "counts":
                histogram = obj.get("vs")
        if size and histogram:
            return SensorDataPoint(
                time=event.receiveTimeStamp,
                sensorId=sensorId,
                size=size,
                histogram=histogram,
            )
