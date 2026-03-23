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


class TimestampsRecoverer:

    def __init__(self, sensorEvents: SensorEvents):
        self.sensorEvents = sensorEvents

    def recoverTimestamps(self) -> SensorEvents:
        recoveredEvents = []
        receiveIntervalQuantile = self.sensorEvents.getReceiveIntervalQuantile(0.9)
        receiveDelayQuantile = self.sensorEvents.getReceiveDelayQuantile(0.9)
        sensorUpdateTime = self.sensorEvents.getSensorUpdateTime()

        events = self.sensorEvents.events
        for index in range(len(events) - 1):
            currentEvent = self.sensorEvents(index)
            nextEvent = self.sensorEvents(index + 1)

            currentSensorTimestamp = currentEvent.sensorTimestamp
            currentReceiveTimestamp = currentEvent.receiveTimestamp

            # If sensorTimestamp exist
            if currentSensorTimestamp:
                delaySensorReceive = currentReceiveTimestamp - currentSensorTimestamp
                # If sensorTimestamp is in sync with receiveTimestamp (No anomalies)
                # if delaySensorReceive > receiveIntervalQuantile:
                #     currentEvent.sensorTimestamp = currentReceiveTimestamp
                #   If it is in sync with receiveTimestamp:
                #     Use it.
                #   Else:
                #     Sync it with receiveTimestamp
            else:
                nextReceiveTimestamp = nextEvent.receiveTimestamp
                receiveTimeInterval = nextReceiveTimestamp - currentReceiveTimestamp

                # If Delay between timestamp is within 90 quantile of the delays use the receiveTimestamp as sensorTimestamp.
                if receiveTimeInterval <= receiveIntervalQuantile:
                    currentEvent.sensorTimestamp = currentReceiveTimestamp
                else:
                    if (
                        currentReceiveTimestamp < sensorUpdateTime
                    ):  # Accumulated histogram
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
