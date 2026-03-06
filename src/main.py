import typer
from enum import StrEnum
from repository.storage import StorageType
from data_service import DataService
import os

app = typer.Typer()
dataService = DataService()


@app.command()
def migrate(
    fDB=StorageType.DIRECTORY,
    tDB=StorageType.FILE,
    fromPath="./data",
    toPath="./out",
):
    dataService.migrateDirectoryToFile(fromPath)


@app.command()
def sensors(
    dataPath="./data",
):
    sensors = dataService.getAllSensors(dataPath)
    print(sensors)


@app.command()
def plotTime(
    sensorId: str = "",
):
    dataService.plotReceiveTimeVsSensorTime(sensorId)


if __name__ == "__main__":
    app()
