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
from models.sensor_event import SensorEvent, SensorEvents
import numpy as np


class DataRecovery:

    def __init__(self, sensorEvents: SensorEvents):
        self.sensorEvents = sensorEvents

    def recoverReceiveTimestamps(self) -> SensorEvents:
        recoveredEvents = []

        # tz = timezone("Europe/Stockholm")
        # tz.__u

        startDate = events[0].receiveTimestamp
        endDate = events[len(events)].receiveTimestamp

        events = self.sensorEvents.events
        for event in events:
            pass
        return recoveredEvents

    def recoverSensorTimestamps(self) -> SensorEvents:
        recoveredEvents = []
        receiveIntervalMeanValue = (
            self.sensorEvents.getReceiveIntervalMeanValueWithinQuantile(0.9)
        )
        receiveIntervalQuantile = self.sensorEvents.getReceiveIntervalQuantile(0.9)
        receiveDelayQuantile = self.sensorEvents.getReceiveDelayQuantile(0.9)
        sensorUpdateTime = self.sensorEvents.getSensorUpdateTime()

        events = self.sensorEvents.events
        for index in range(1, len(events)):
            currentEvent = self.sensorEvents(index)
            prevEvent = self.sensorEvents(index - 1)

            currentSensorTimestamp = currentEvent.sensorTimestamp
            currentReceiveTimestamp = currentEvent.receiveTimestamp

            # If sensorTimestamp exist
            if currentSensorTimestamp:
                receiveDelay = currentReceiveTimestamp - currentSensorTimestamp
                # If sensorTimestamp is in sync with receiveTimestamp (No anomalies)
                # if delaySensorReceive > receiveIntervalQuantile:
                #     currentEvent.sensorTimestamp = currentReceiveTimestamp
                #   If it is in sync with receiveTimestamp:
                #     Use it.
                #   Else:
                #     Sync it with receiveTimestamp
            else:
                prevReceiveTimestamp = prevEvent.receiveTimestamp
                receiveInterval = currentReceiveTimestamp - prevReceiveTimestamp

                # If Delay between timestamp is within quantile of the delays use the receiveTimestamp as sensorTimestamp.
                if receiveInterval <= receiveIntervalQuantile:
                    currentEvent.sensorTimestamp = currentReceiveTimestamp
                else:
                    if (
                        currentReceiveTimestamp < sensorUpdateTime
                    ):  # Accumulated histogram
                        if netError:
                            currentEvent.sensorTimestamp = currentReceiveTimestamp
                        else:  # Lost data
                            pass
                    else:  # Fresh histogram measurements
                        if netError:
                            pass
                        else:  # Lost data
                            pass

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
