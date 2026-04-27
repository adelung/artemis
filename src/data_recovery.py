from dataclasses import replace
from models.sensor_log_event import SensorLogEvent
from models.sensor_event import SensorEvent, SensorEvents, EventType, SensorHistogram
from datetime import timedelta, datetime, timezone
from zoneinfo import ZoneInfo
import numpy as np


class DataRecovery:
    """
    DataRecovery class is responsible for various recovery methods used to recover sensor
    timestamps. eg. DST misalignments and missing sensor timestamps.
    """

    def __init__(self, sensorEvents: SensorEvents):
        self.sensorEvents = sensorEvents

    def recoverReceiveTime(self) -> SensorEvents:
        """
        Recover overlapping or jumping receive time during the 1 hour DST time shift.
        """

        events = self.sensorEvents.events
        startDate = datetime.fromtimestamp(events[0].receiveTimestamp)
        endDate = datetime.fromtimestamp(events[-1].receiveTimestamp)
        latched = False
        latchUntil = None
        countFixes = 0
        countStartTime = None
        for index in range(1, len(events)):

            prevEvent = events[index - 1]
            prevEventTimestamp = datetime.fromtimestamp(
                prevEvent.receiveTimestamp, tz=ZoneInfo("Europe/Stockholm")
            )
            currentEvent = events[index]
            currentEventTimestamp = datetime.fromtimestamp(
                currentEvent.receiveTimestamp, tz=ZoneInfo("Europe/Stockholm")
            )

            if currentEventTimestamp < prevEventTimestamp or latched:
                if not latchUntil:
                    countStartTime = currentEventTimestamp
                    latchUntil = currentEventTimestamp.replace(
                        minute=0,
                        second=0,
                        microsecond=0,
                    ) + timedelta(hours=1)
                latched = currentEventTimestamp < latchUntil
                currentEventTimestamp = currentEventTimestamp.replace(fold=1)
                currentEvent.receiveTimestamp = currentEventTimestamp.timestamp()
                countFixes += 1

        print(f"{countFixes} ReceiveTimestamps adjusted starting from {countStartTime}")
        return self.sensorEvents

    def spreadSensorTimestamp(
        self,
        currentReceiveTimestamp,
        clumpReceiveIntervalThreshold,
        receiveIntervalMean,
        histogramEvents,
    ):
        """
        Spreads the clumped received timestamps within a clumpReceiveIntervalThreshold
        by receiveIntervalMean and sets the sensor timestamp respectively.
        """

        adjacentHistogramTimeMin = (
            currentReceiveTimestamp - clumpReceiveIntervalThreshold
        )
        adjacentHistogramTimeMax = (
            currentReceiveTimestamp + clumpReceiveIntervalThreshold
        )
        adjacentHistograms = list(
            filter(
                (
                    lambda event: event.receiveTimestamp > adjacentHistogramTimeMin
                    and event.receiveTimestamp < adjacentHistogramTimeMax
                ),
                histogramEvents,
            )
        )
        for i, event in enumerate(reversed(adjacentHistograms)):
            event.sensorTimestamp = int(
                adjacentHistogramTimeMax - i * receiveIntervalMean
            )

    def recoverSensorTime(self) -> SensorEvents:
        _, receiveIntervalMax, receiveIntervalMean = (
            self.sensorEvents.getReceiveIntervalRange(0.98)
        )
        """
        Recover sensor time stamp according to:
        # compare receiveTimestamp with previous receiveTimestamp.
        #   If Interval between receiveTimestamp is within 90 quantile of the period:
        #     use the receiveTimestamp as sensorTimestamp.
        #   Else:
        #     Separate data when before and after update:
        #     If Histogram has accumulated data (Before update):
        #       Detect error type by checking radon histogram values.
        #       If Net error (Histogram not reset):
        #         Many histograms with almost same receiveTimestamp: Spread
        #       Else If sensor error (Histogram reset to zero):
        #         Lost data
        #     Else fresh measurement (After update):
        #       Many histograms with almost same receiveTimestamp: Spread
        """

        clumpReceiveIntervalThreshold = receiveIntervalMean / 2
        sensorUpdateTime = self.sensorEvents.getSensorUpdateTime()

        print(
            f"=== Recovering sensor timestamp for sensor {self.sensorEvents.sensorId} update time: {sensorUpdateTime} {datetime.fromtimestamp(sensorUpdateTime, tz=ZoneInfo("Europe/Stockholm"))} ==="
        )

        histogramEvents = self.sensorEvents.histogramEvents().events
        events = self.sensorEvents.events
        for index in range(1, len(events)):
            currentEvent = events[index]
            prevEvent = events[index - 1]

            currentReceiveTimestamp = currentEvent.receiveTimestamp
            prevReceiveTimestamp = prevEvent.receiveTimestamp

            # If receiveInterval is reasonable use receive timestamp as sensor timestamp
            receiveInterval = currentReceiveTimestamp - prevReceiveTimestamp
            if receiveInterval <= receiveIntervalMax:
                currentEvent.sensorTimestamp = currentReceiveTimestamp
            else:
                beforeUpdate = currentReceiveTimestamp < sensorUpdateTime
                print(
                    f"Receive interval {receiveInterval} at {currentReceiveTimestamp} {datetime.fromtimestamp(currentReceiveTimestamp, tz=ZoneInfo("Europe/Stockholm"))} {"before" if beforeUpdate else "after" } update"
                )
                # Accumulated histogram
                if beforeUpdate:
                    eventType = currentEvent.eventType
                    if eventType == EventType.HISTOGRAM:
                        histogramEventIndex = next(
                            (
                                i
                                for i, event in enumerate(histogramEvents)
                                if event.receiveTimestamp == currentReceiveTimestamp
                            ),
                            None,
                        )
                        histogramPrevEvent = histogramEvents[histogramEventIndex - 1]
                        currentHistogram = SensorHistogram(
                            **currentEvent.load
                        ).histogram
                        prevHistogram = SensorHistogram(
                            **histogramPrevEvent.load
                        ).histogram
                        difference = np.subtract(currentHistogram, prevHistogram)
                        negative = any(value < 0 for value in difference)
                        allZero = all(value == 0 for value in currentHistogram)

                        # Sensor crash Probably
                        if allZero or negative:
                            print(f"Sensor restarted! Setting received event timestamp")
                            currentEvent.sensorTimestamp = currentReceiveTimestamp
                        # Lost connection probably
                        else:
                            print(
                                f"Connection lost! Distributing clumped events receive timestamp"
                            )
                            self.spreadSensorTimestamp(
                                currentReceiveTimestamp,
                                clumpReceiveIntervalThreshold,
                                receiveIntervalMean,
                                events,
                            )

                # Fresh histogram measurements
                else:
                    self.spreadSensorTimestamp(
                        currentReceiveTimestamp,
                        clumpReceiveIntervalThreshold,
                        receiveIntervalMean,
                        events,
                    )

        return self.sensorEvents

    def flattenHistogram(self) -> SensorEvents:
        """
        Flattening radon histogram data for the radon sensor measurements before updating
        the sensors. Each radon measurement is subtracted from the previous measurement
        and the difference is used as the measured value during that time interval.
        """

        flattenedHistogramEvents = list[SensorEvent]()
        sensorUpdateTime = self.sensorEvents.getSensorUpdateTime()
        events = self.sensorEvents.histogramEvents().beforeUpdateEvents().events

        if len(events) == 0:
            return self.sensorEvents

        firstEvent = events[0]
        firstEventLoad = firstEvent.load
        firstHistogramLength = len(firstEventLoad.get("histogram"))
        zeroHistogram = SensorHistogram(
            firstHistogramLength, histogram=[0 for i in range(firstHistogramLength)]
        )
        flattenedHistogramEvents.append(zeroHistogram)

        for index in range(1, len(events)):
            currentEvent = events[index]
            prevEvent = events[index - 1]

            currentReceiveTimestamp = currentEvent.receiveTimestamp
            prevReceiveTimestamp = prevEvent.receiveTimestamp
            beforeUpdate = currentReceiveTimestamp < sensorUpdateTime

            currentLoad = currentEvent.load
            currentHistogram = (
                currentLoad
                if isinstance(currentLoad, SensorHistogram)
                else SensorHistogram(**currentLoad)
            ).histogram
            prevLoad = prevEvent.load
            prevHistogram = (
                prevLoad
                if isinstance(prevLoad, SensorHistogram)
                else SensorHistogram(**prevLoad)
            ).histogram
            difference = np.subtract(currentHistogram, prevHistogram)
            negative = any(value < 0 for value in difference)
            allZero = all(value == 0 for value in currentHistogram)

            sensorHistogram = None
            # Sensor crash Probably
            if not (allZero or negative):
                sensorHistogram = SensorHistogram(len(difference), difference.tolist())
            else:
                sensorHistogram = currentEvent.load

            flattenedHistogramEvents.append(sensorHistogram)

        for index, event in enumerate(events):
            event.load = flattenedHistogramEvents[index]

        return self.sensorEvents
