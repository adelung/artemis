# Data structure and aggregator for the sensor events for processing.

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from enum import StrEnum
from models.serializable import Serializable
from urnparse import URN8141
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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


# Data classes mapping the sensor event measurement in order to be processed.
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
    histogram: list[int]


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
    """
    SensorEvent is the main data structure modeling a sensor event while the data is being processed.
    """

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
        """
        Return True if this sensor event after updating the sensor.
        """
        urn = URN8141.from_string(self.urn)
        urnParts = urn.specific_string.parts
        device = next(iter(urnParts[1:2]), None)
        eventTypeString = next(iter(urnParts[2:3]), None)
        return device != "gw" and bool(eventTypeString)

    def isHistogramEvent(self) -> bool:
        """
        Return True if this sensor event is a radon sensor event.
        """
        return self.eventType == EventType.HISTOGRAM


class SensorEvents:
    """
    Aggregator for sensor event in order to process consecutive events or plot the data series.
    """

    def __init__(self, sensorId: str, events: list[SensorEvent]):
        self.sensorId = sensorId
        self.events = events

    def getReceiveDelayRange(self, quantile: float) -> (int, int, float):
        """
        Return the range and mean value of the delays between sensor timestamps and receive timestamps within quantile.
        """
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

    def getReceiveIntervalRange(self, quantile: float) -> (int, int, float):
        """
        Return the range and mean value of the interval between consecutive receive timestamps within quantile.
        """
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
        """
        Computes the min, max and mean value of the distribution.
        """
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
        """
        Returns the update time of the sensor.
        """
        firstEventAfterUpdateIndex = next(
            (i for i, event in enumerate(self.events) if event.isUpdatedSensorEvent()),
            None,
        )
        if firstEventAfterUpdateIndex is None:
            lastEventBeforeUpdateIndex = next(
                (
                    i
                    for i, event in enumerate(reversed(self.events))
                    if not event.isUpdatedSensorEvent()
                ),
                None,
            )
            return self.events[
                len(self.events) - (lastEventBeforeUpdateIndex + 1)
            ].receiveTimestamp
        else:
            return self.events[firstEventAfterUpdateIndex].receiveTimestamp

    def histogramEvents(self) -> "SensorEvents":
        """
        Returns SensorEvents with only the radon histogram events in it.
        """
        return SensorEvents(
            self.sensorId,
            [event for event in self.events if event.isHistogramEvent()],
        )

    def noneHistogramEvents(self) -> "SensorEvents":
        """
        Returns SensorEvents without the radon histogram events in it.
        """
        return SensorEvents(
            self.sensorId,
            [event for event in self.events if not event.isHistogramEvent()],
        )

    def noneStatusEvents(self) -> "SensorEvents":
        """
        Returns SensorEvents without the sensor status events in it.
        """
        return SensorEvents(
            self.sensorId,
            [event for event in self.events if "gw" not in event.urn],
        )

    def beforeUpdateEvents(self) -> "SensorEvents":
        """
        Returns SensorEvents prior to the sensor update.
        """
        updateTime = self.getSensorUpdateTime()
        return SensorEvents(
            self.sensorId,
            [event for event in self.events if event.receiveTimestamp < updateTime],
        )

    def afterUpdateEvents(self) -> "SensorEvents":
        """
        Returns SensorEvents after to the sensor update.
        """
        updateTime = self.getSensorUpdateTime()
        return SensorEvents(
            self.sensorId,
            [event for event in self.events if event.receiveTimestamp > updateTime],
        )

    def toIso(self) -> "SensorEvents":
        """
        Returns SensorEvents with the dates presented in ISO.
        """
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
        """
        Returns True if SensorEvents is empty.
        """
        return len(self.events) == 0

    def plotSensorCaptures(self):
        """
        Plot SensorEvents sensor timestamps.
        """
        captureTimes = []
        for index in range(len(self.events) - 1):
            currentEvent = self.events[index]
            currentEventTimestamp = currentEvent.sensorTimestamp
            if currentEventTimestamp:
                captureTimes.append(currentEventTimestamp)
        self.plotDateGraph(
            captureTimes,
            range(len(captureTimes)),
            f"Sensor measurements of {self.sensorId}",
            "Epoch",
            "Event #",
        )

    def plotSensorTimeInterval(self):
        """
        Plot SensorEvents consecutive sensor timestamps interval in a bar chart.
        """
        timeDistribution = []
        for index in range(len(self.events) - 1):
            currentEvent = self.events[index]
            currentEventTimestamp = currentEvent.sensorTimestamp
            nextEvent = self.events[index + 1]
            nextEventTimestamp = nextEvent.sensorTimestamp
            if currentEventTimestamp and nextEventTimestamp:
                interval = nextEventTimestamp - currentEventTimestamp
                timeDistribution.append(interval)
            if interval < 0:
                print(
                    f"Event: {currentEventTimestamp} {datetime.fromtimestamp(currentEventTimestamp, tz=ZoneInfo("Europe/Stockholm"))} Interval: {interval}"
                )
        self.plotBarChart(
            timeDistribution,
            f"Sensor interval histogram of {self.sensorId}",
            "Interval [s]",
            "Count [#]",
        )

    def plotReceiveDelay(self, upTo: float):
        """
        Plot receive delay between sensor and receive timestamps in a bar chart.
        """
        timeDistribution = []
        for event in self.events:
            sensorTimestamp = event.sensorTimestamp
            if event.sensorTimestamp:
                receiveTimestamp = event.receiveTimestamp
                delay = receiveTimestamp - sensorTimestamp
                if delay <= upTo:
                    timeDistribution.append(delay)
        self.plotBarChart(
            timeDistribution,
            f"Delay histogram of {self.sensorId}",
            "Delay [s]",
            "Count [#]",
            log=True,
        )

    def plotReceiveInterval(self, upTo: float):
        """
        Plot receive delay between consecutive receive timestamps in a bar chart.
        """
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
        self.plotBarChart(
            timeDistribution,
            f"Receive interval histogram of {self.sensorId}",
            "Interval [s]",
            "Count [#]",
            log=True,
        )

    def plotRadonHistogram(self):
        """
        Plot radon histogram.
        """
        sensorTimestamps = list[int]()
        histograms = list[float]()
        histogramEvents = self.histogramEvents().events
        for event in histogramEvents:
            sensorTime = event.sensorTimestamp
            if sensorTime:
                sensorTimestamps.append(datetime.fromtimestamp(sensorTime))
                histogram = SensorHistogram(**event.load).histogram
                histogramIntegral = np.sum(histogram)
                histograms.append(histogramIntegral)
        self.plotDateGraph(
            sensorTimestamps,
            histograms,
            f"Radon measurements of {self.sensorId}",
            "Sensor time",
            "Radon integral",
        )

    def plotBarChart(
        self, distribution, title: str, xLabel: str, yLabel: str, log=False
    ):
        fig, ax = plt.subplots()
        ax.hist(distribution, bins="auto", edgecolor="grey", alpha=0.7)
        plt.title(title)
        plt.xlabel(xLabel)
        plt.ylabel(yLabel)
        # plt.xlim(0, 1000)
        plt.grid(True, alpha=0.3)
        if log:
            # plt.xscale("log")
            plt.yscale("log")
        self.addCursor(ax)
        plt.show()

    def plotDateGraph(self, x, y, title: str, xLabel: str, yLabel: str):
        fig, ax = plt.subplots()
        ax.plot(x, y, ".")
        # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        # plt.gcf().autofmt_xdate()
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
