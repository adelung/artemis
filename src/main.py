import typer
from enum import StrEnum
from repository.storage import StorageType
from data_service import DataService
import os

app = typer.Typer()
dataService = DataService()


@app.command()
def collectToFile(
    dataPath="./data",
):
    dataService.migrateDirectoryToFile(dataPath)


@app.command()
def sensors(
    dataPath="./data",
):
    sensors = dataService.getAllSensors(dataPath)
    print(sensors)


@app.command()
def plotReceiveDelay(
    sensorId: str = "",
):
    dataService.plotReceiveDelay(sensorId)


@app.command()
def plotTimeGap(
    dataPath="./data",
    sensorId: str = "",
):
    if sensorId == "":
        for sensor in dataService.getAllSensors(dataPath):
            dataService.plotTimeGap(sensor)
    else:
        dataService.plotTimeGap(sensorId)


@app.command()
def migrate(
    dataPath="./data",
    sensorId: str = "",
):
    dataService.migrateDataToInfluxDB(dataPath, sensorId)


if __name__ == "__main__":
    app()
