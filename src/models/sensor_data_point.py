# Data class for storing sensor events on InfluxDB.

from dataclasses import dataclass
from datetime import datetime
from typing import Self
from models.serializable import Serializable
from models.sensor_event import SensorEvent
import numpy as np


@dataclass
class SensorDataPoint(Serializable["SensorDataPoint"]):
    """
    SensorDataPoint is the data structure used for exporting the data to InfluxDB to match the required data there.
    """

    time: datetime
    sensorId: str
    size: int
    histogram: str
    integral: int

    def fromSensorEvent(sensorId: str, event: SensorEvent) -> Self:
        """
        Converts SensorEvent to SensorDataPoint.
        """
        load = event.load
        size = None
        histogram = None
        for obj in load:
            if obj.get("n") == "size":
                size = obj.get("v")
            if obj.get("n") == "counts":
                histogram = obj.get("vs")
        if size is not None and histogram is not None:
            time = event.receiveTimestamp
            return SensorDataPoint(
                time=time * 1000 if time < 9999999999 else time,
                sensorId=sensorId,
                size=size,
                histogram=histogram,
                integral=np.sum(histogram),
            )
