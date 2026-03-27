# Data structure and aggregator for the sensor events for processing.

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from enum import StrEnum
from models.serializable import Serializable
from urnparse import URN8141
import matplotlib.pyplot as plt
import mplcursors
import numpy as np


class EventType(StrEnum):
    HISTOGRAM = "histogram"
    PHT = "pht"
    acc = "acc"
    GYRO = "gyro"
    MAG = "mag"
    EC = "ec"
    P = "p"
    MIC = "mic"


@dataclass
class SensorMeasurement(Serializable["SensorMeasurement"]):

    # name: str
    value: float
    unit: str | None


@dataclass
class SensorGatewayStatus:

    bn: str


@dataclass
class SensorHistogram:

    size: int
    histogram: list[float]


@dataclass
class SensorPHT:

    pressure: SensorMeasurement
    humidity: SensorMeasurement
    temperature: SensorMeasurement
    # TODO: a stand for what?
    a: SensorMeasurement


@dataclass
class SensorAccelerometer:

    x: SensorMeasurement
    y: SensorMeasurement
    z: SensorMeasurement
    temperature: SensorMeasurement


@dataclass
class SensorGyroscope:

    x: SensorMeasurement
    y: SensorMeasurement
    z: SensorMeasurement


@dataclass
class SensorMagnet:

    x: SensorMeasurement
    y: SensorMeasurement
    z: SensorMeasurement


@dataclass
class SensorEC:

    value: float


@dataclass
class SensorP:

    value: float


@dataclass
class SensorMic:

    value: float


@dataclass
class SensorEvent(Serializable["SensorEvent"]):

    receiveTimestamp: datetime | int
    sensorTimestamp: datetime | int
    urn: str
    eventType: EventType
    load: (
        SensorGatewayStatus
        | SensorHistogram
        | SensorPHT
        | SensorAccelerometer
        | SensorGyroscope
        | SensorMagnet
        | SensorEC
        | SensorP
        | SensorMic
    )

    def isUpdatedSensorEvent(self) -> bool:
        urn = URN8141.from_string(self.urn)
        urnParts = urn.specific_string.parts
        device = next(iter(urnParts[1:2]), None)
        eventTypeString = next(iter(urnParts[2:3]), None)
        return device != "gw" and bool(eventTypeString)

    def isHistogramEvent(self) -> bool:
        return "histogram" in self.urn


class SensorEvents:

    def __init__(self, sensorId: str, events: list[SensorEvent]):
        self.sensorId = sensorId
        self.events = events

    def getReceiveDelayRange(self, quantile: float) -> (int, int, float):
        distribution = [
            event.receiveTimestamp - event.sensorTimestamp
            for event in self.events
            if event.sensorTimestamp
        ]
        min, max, mean = self._calcMinMaxMean(distribution, quantile)
        print(
            f"Receive delay mean: {mean}, range: {min} - {max} for sensor: {self.sensorId}"
        )
        return min, max, mean

    def getReceiveIntervalRange(self, quantile: float) -> float:
        distribution = [
            self.events[index + 1].receiveTimestamp
            - self.events[index].receiveTimestamp
            for index in range(len(self.events) - 1)
        ]
        min, max, mean = self._calcMinMaxMean(distribution, quantile)
        print(
            f"Receive interval mean: {mean}, range: {min} - {max} for sensor: {self.sensorId}"
        )
        return min, max, mean

    def _calcMinMaxMean(self, distribution: list[int], quantile: float) -> list[int]:
        quantileValue = np.quantile(distribution, quantile)
        qLower = np.quantile(distribution, 1 - quantile)
        qUpper = np.quantile(distribution, quantile)
        quantileRange = qUpper - qLower
        lowerBound = qLower - 1.5 * quantileRange
        upperBound = qUpper + 1.5 * quantileRange
        filteredDistribution = list(
            filter(
                lambda value: value >= lowerBound and value <= upperBound, distribution
            )
        )
        min = np.min(filteredDistribution)
        max = np.max(filteredDistribution)
        mean = np.mean(filteredDistribution)
        return min, max, mean

    def getSensorUpdateTime(self) -> datetime:
        firstEventAfterUpdateIndex = next(
            (i for i, event in enumerate(self.events) if event.isUpdatedSensorEvent()),
            None,
        )
        if firstEventAfterUpdateIndex is not None:
            return self.events[firstEventAfterUpdateIndex].receiveTimestamp

    def histogramEvents(self) -> "SensorEvents":
        return SensorEvents(
            self.sensorId,
            [event for event in self.events if event.isHistogramEvent()],
        )

    def noneStatusEvents(self) -> "SensorEvents":
        return SensorEvents(
            self.sensorId,
            [event for event in self.events if "gw" not in event.urn],
        )

    def toIso(self) -> "SensorEvents":
        return SensorEvents(
            self.sensorId,
            [
                replace(
                    event,
                    receiveTimestamp=datetime.fromtimestamp(
                        event.receiveTimestamp, tz=ZoneInfo("Europe/Stockholm")
                    ),
                    sensorTimestamp=(
                        datetime.fromtimestamp(
                            int(event.sensorTimestamp), tz=timezone.utc
                        )
                        if event.sensorTimestamp and event.sensorTimestamp <= 9999999999
                        else None
                    ),
                )
                for event in self.events
            ],
        )

    def empty(self) -> bool:
        return len(self.events) == 0

    def plotReceiveDelay(self, upTo: float):
        timeDistribution = []
        for event in self.events:
            load = event.load
            sensorTimestamp = event.sensorTimestamp
            if event.sensorTimestamp:
                receiveTimestamp = event.receiveTimestamp
                delay = receiveTimestamp - sensorTimestamp
                if delay <= upTo:
                    timeDistribution.append(delay)
        self.plotHistogram(
            timeDistribution,
            f"Delay histogram of {self.sensorId}",
            "Delay [s]",
            "Count [#]",
        )

    def plotReceiveInterval(self, upTo: float):
        print(f"Plotting receive interval upto: {upTo} ignoring events bellow:")
        timeDistribution = []
        for index in range(len(self.events) - 1):
            currentEvent = self.events[index]
            currentEventTimestamp = currentEvent.receiveTimestamp
            nextEvent = self.events[index + 1]
            nextEventTimestamp = nextEvent.receiveTimestamp
            interval = nextEventTimestamp - currentEventTimestamp
            if interval <= upTo:
                timeDistribution.append(interval)
            else:
                print(
                    f"Event: {currentEventTimestamp} {datetime.fromtimestamp(currentEventTimestamp, tz=ZoneInfo("Europe/Stockholm"))} Interval: {interval}"
                )
            # if delay > 60 * 60:
            #     currentHistogram = currentEvent.load.histogram
            #     nextHistogram = nextEvent.load.histogram
            #     if currentHistogram and nextHistogram:
            #         result = np.subtract(nextHistogram, currentHistogram)
            #         print(
            #             f"Delay: {delay/3600}, Epoch: {currentEventTimestamp} Iso: {datetime.fromtimestamp(currentEventTimestamp).isoformat()}"
            #         )
            #         print(result)
            #         print("-----------------------------")
        self.plotHistogram(
            timeDistribution,
            f"Interval histogram of {self.sensorId}",
            "Interval [s]",
            "Count [#]",
        )

    def plotHistogram(self, distribution, title: str, xLabel: str, yLabel: str):
        fig, ax = plt.subplots()
        ax.hist(distribution, bins="auto", edgecolor="grey", alpha=0.7)
        plt.title(title)
        plt.xlabel(xLabel)
        plt.ylabel(yLabel)
        plt.grid(True, alpha=0.3)
        self.addCursor(ax)
        plt.show()

    def addCursor(self, ax):
        cursor = mplcursors.cursor(ax, hover=True)
        cursor.connect(
            "add",
            lambda sel: sel.annotation.set_text(
                f"x={sel.target[0]:.2f}, y={sel.target[1]:.2f}"
            ),
        )
