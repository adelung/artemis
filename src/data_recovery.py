# If sensorTimestamp exist:
#   If it is in sync with receiveTimestamp:
#     Use it.
#   Else:
#     Sync it with receiveTimestamp by shifting the sensorTimestamp the interrupt amount of time to receiveTimestamp.
# Else compare receiveTimestamp with previous receiveTimestamp.
#   If Interval between receiveTimestamp is within 90 quantile of the period:
#     use the receiveTimestamp as sensorTimestamp.
#   Else:
#     Separate data when accumulation is gone by comparing the sensor name and obj.bn:
#     If Histogram has accumulated data (Dataset 1):
#       If Net error:
#         One large histogram or many histograms with almost same receiveTimestamp.
#       Else If sensor error:
#         Lost data
#     Else fresh measurement (Dataset 2):
#       If Net error:
#         Many histograms.
#       Else If sensor error:
#         Lost data.

from models.sensor_log_event import SensorLogEvent
from models.sensor_event import SensorEvent, SensorEvents, EventType, SensorHistogram
from datetime import timedelta, datetime, timezone
from zoneinfo import ZoneInfo
import numpy as np


class DataRecovery:

    def __init__(self, sensorEvents: SensorEvents):
        self.sensorEvents = sensorEvents

    def recoverReceiveTime(self) -> SensorEvents:
        print(f"=== Adjusting DST for sensor {self.sensorEvents.sensorId} ===")
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

    def recoverSensorTime(self) -> SensorEvents:
        print(
            f"=== Recovering sensor timestamp for sensor {self.sensorEvents.sensorId} ==="
        )

        recoveredEvents = []

        _, receiveIntervalMax, _ = self.sensorEvents.getReceiveIntervalRange(0.9)
        sensorUpdateTime = self.sensorEvents.getSensorUpdateTime()
        print(
            f"Sensor update time: {sensorUpdateTime} {datetime.fromtimestamp(sensorUpdateTime, tz=ZoneInfo("Europe/Stockholm"))}"
        )

        events = self.sensorEvents.events
        for index in range(1, len(events)):
            currentEvent = events[index]
            prevEvent = events[index - 1]

            currentSensorTimestamp = currentEvent.sensorTimestamp
            currentReceiveTimestamp = currentEvent.receiveTimestamp

            prevSensorTimestamp = prevEvent.sensorTimestamp
            prevReceiveTimestamp = prevEvent.receiveTimestamp

            # If receiveInterval is reasonable
            receiveInterval = currentReceiveTimestamp - prevReceiveTimestamp
            if receiveInterval <= receiveIntervalMax:
                currentEvent.sensorTimestamp = currentReceiveTimestamp
            else:
                if currentReceiveTimestamp < sensorUpdateTime:  # Accumulated histogram
                    print(
                        f"Receive Interval {receiveInterval} at {currentReceiveTimestamp} before update"
                    )
                    eventType = currentEvent.eventType
                    if eventType == EventType.HISTOGRAM:
                        histogram: SensorHistogram = currentEvent.load
                        print(histogram)

                #     if netError:
                #         pass
                #         # currentEvent.sensorTimestamp = currentReceiveTimestamp
                #     else:  # Lost data
                #         pass
                else:  # Fresh histogram measurements
                    print(
                        f"Receive Interval {receiveInterval} at {currentReceiveTimestamp} after update"
                    )

                #     if netError:
                #         pass
                #     else:  # Lost data
                #         pass

        return recoveredEvents


# Else compare receiveTimestamp with previous receiveTimestamp.
#   If Interval between receiveTimestamp is within 90 quantile of the period:
#     use the receiveTimestamp as sensorTimestamp.
#   Else:
#     Separate data when accumulation is gone by comparing the sensor name and obj.bn:
#     If Histogram has accumulated data (Dataset 1):
#       If Net error:
#         One large histogram or many histograms with almost same receiveTimestamp.
#       Else If sensor error:
#         Lost data
#     Else fresh measurement (Dataset 2):
#       If Net error:
#         Many histograms.
#       Else If sensor error:
#         Lost data.
