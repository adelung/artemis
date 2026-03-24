# Data structure and aggregator for the sensor events for processing.

from dataclasses import dataclass
from datetime import datetime, timezone
from models.serializable import Serializable
import matplotlib.pyplot as plt
import mplcursors
import numpy as np


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

    receiveTimestamp: int
    sensorTimestamp: int
    urn: str
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
    new = True


class SensorEvents:

    def __init__(self, sensorId: str, events: list[SensorEvent]):
        self.sensorId = sensorId
        self.events = events

    def getReceiveIntervalQuantile(self, quantile: float) -> float:
        distribution = [
            self.events[index + 1].receiveTimestamp
            - self.events[index].receiveTimestamp
            for index in range(len(self.events) - 1)
        ]
        quantileValue = np.quantile(distribution, quantile)
        # print(f"sensorId: {self.sensorId} quantileValue: {quantileValue}")
        # distribution = [value for value in distribution if abs(value) < quantileValue]
        # fig, ax = plt.subplots()
        # ax.hist(distribution, bins="auto", edgecolor="grey", alpha=0.7)
        # plt.grid(True, alpha=0.3)
        # self.addCursor(ax)
        # plt.show()
        return quantileValue

    def getReceiveDelayQuantile(self, quantile: float) -> float:
        distribution = [
            event.receiveTimestamp - event.sensorTimestamp
            for event in self.events
            if event.sensorTimestamp
        ]
        quantileValue = np.quantile(distribution, quantile)
        # print(f"sensorId: {self.sensorId} quantileValue: {quantileValue}")
        # distribution = [value for value in distribution if abs(value) < quantileValue]
        # fig, ax = plt.subplots()
        # ax.hist(distribution, bins="auto", edgecolor="grey", alpha=0.7)
        # plt.grid(True, alpha=0.3)
        # self.addCursor(ax)
        # plt.show()
        return quantileValue

    def getReceiveIntervalMeanValueWithinQuantile(self, quantile: float) -> float:
        distribution = [
            self.events[index + 1].receiveTimestamp
            - self.events[index].receiveTimestamp
            for index in range(len(self.events) - 1)
        ]
        qLower = np.quantile(distribution, 1 - quantile)
        qUpper = np.quantile(distribution, quantile)
        quantileRange = qUpper - qLower
        lowerBound = qLower
        upperBound = qUpper
        filteredDistribution = list(
            filter(
                lambda value: value >= lowerBound and value <= upperBound, distribution
            )
        )
        meanValue = np.mean(filteredDistribution)
        # print(f"sensorId: {self.sensorId} quantileValue: {quantileValue}")
        # distribution = [value for value in distribution if abs(value) < quantileValue]
        # fig, ax = plt.subplots()
        # ax.hist(distribution, bins="auto", edgecolor="grey", alpha=0.7)
        # plt.grid(True, alpha=0.3)
        # self.addCursor(ax)
        # plt.show()
        return meanValue

    # TODO: Maybe return another event (like pressure of gyro) timestamp instead of receiveTimestamp.
    def getSensorUpdateTime(self) -> datetime:
        firstEventAfterUpdateIndex = next(
            (i for i, event in enumerate(self.events) if event.isUpdatedSensorEvent()),
            None,
        )
        if firstEventAfterUpdateIndex:
            return self.events[firstEventAfterUpdateIndex - 1].receiveTimestamp

    def histogramEvents(self) -> "SensorEvents":
        return SensorEvents(
            self.sensorId,
            [event for event in self.events if "histogram" in event.urn],
        )

    def noneStatusEvents(self) -> "SensorEvents":
        return SensorEvents(
            self.sensorId,
            [event for event in self.events if "gw" not in event.urn],
        )

    def plotReceiveDelay(self, upTo: float):
        timeDistribution = []
        for event in self.events:
            load = event.load
            sensorTimestamp = event.sensorTimestamp
            if event.sensorTimestamp:
                receiveTimestamp = event.receiveTimestamp
                delay = receiveTimestamp - sensorTimestamp
                if delay < upTo:
                    timeDistribution.append(delay)
        fig, ax = plt.subplots()
        ax.hist(timeDistribution, bins="auto", edgecolor="grey", alpha=0.7)
        plt.title(f"Delay Histogram of {self.sensorId}")
        plt.xlabel("Delay [s]")
        plt.ylabel("Count")
        plt.grid(True, alpha=0.3)
        self.addCursor(ax)
        plt.show()

    def plotReceiveInterval(self, upTo: float):
        timeDistribution = []
        for index in range(len(self.events) - 1):
            currentEvent = self.events[index]
            currentEventTimestamp = currentEvent.receiveTimestamp
            nextEvent = self.events[index + 1]
            nextEventTimestamp = nextEvent.receiveTimestamp
            interval = nextEventTimestamp - currentEventTimestamp
            if interval < upTo:
                timeDistribution.append(interval)
            else:
                print(
                    f"Event: {datetime.fromtimestamp(currentEvent.receiveTimestamp, tz=timezone.utc)} Interval: {interval}"
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
        fig, ax = plt.subplots()
        ax.hist(timeDistribution, bins="auto", edgecolor="grey", alpha=0.7)
        plt.title(f"Interval of {self.sensorId}")
        plt.xlabel("Interval [s]")
        plt.ylabel("Count [#]")
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
