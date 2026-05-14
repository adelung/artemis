import typer
from typing import Annotated, Callable
from data_service import DataService
from datetime import datetime

app = typer.Typer()
dataService = DataService("./data")


@app.command()
def sensors():
    """
    List available sensor ids in the data directory.
    """
    sensorsIds = dataService.getAllSensors()
    print(sensorsIds)


@app.command()
def collectToFile(
    sensorId: str = "",
    iso: Annotated[bool, typer.Option("--iso")] = False,
):
    """
    Collect the sensor data to a single file with the sensorId as the name.
    """
    runForAllSensors(
        sensorId,
        lambda id: dataService.collectDirectoryToFile(id, iso),
    )


@app.command()
def recoverData(
    sensorId: str = "",
):
    """
    Run data recovery process.
    """
    runForAllSensors(
        sensorId,
        lambda id: dataService.recoverData(id),
    )


@app.command()
def exportToInfluxDB(
    sensorId: str = "",
    stratTime: datetime = datetime(1970, 1, 1, 0, 0, 0),
    endTime: datetime = datetime.now(),
):
    """
    Export the recovered data to InfluxDB.
    """
    runForAllSensors(
        sensorId,
        lambda id: dataService.exportToInfluxDB(id, startTime, endTime),
    )


@app.command()
def recoverAndMigrate(
    sensorId: str = "",
    stratTime: datetime = datetime(1970, 1, 1, 0, 0, 0),
    endTime: datetime = datetime.now(),
):
    """
    Gathers all sensor data to a file per sensor then recovers the timestamps and lastly exports the data to InfluxDB.
    """
    collectToFile(sensorId)
    recoverData(sensorId)
    exportToInfluxDB(sensorId, startTime, endTime)


@app.command()
def plotReceiveDelay(
    sensorId: str = "",
    recovered: Annotated[bool, typer.Option("--recovered")] = False,
):
    """
    Plot the delay between sensor timestamp and receive timestamp before/after recovering timestamps.
    """
    runForAllSensors(
        sensorId,
        lambda id: dataService.plotReceiveDelay(id, recovered),
    )


@app.command()
def plotSensorCaptures(
    sensorId: str = "",
    recovered: Annotated[bool, typer.Option("--recovered")] = False,
):
    """
    Plot sensor timestamps before/after recovering timestamps.
    """
    runForAllSensors(
        sensorId,
        lambda id: dataService.plotSensorCaptures(id, recovered),
    )


@app.command()
def plotSensorInterval(
    sensorId: str = "",
    recovered: Annotated[bool, typer.Option("--recovered")] = False,
):
    """
    Plot interval between consecutive sensor timestamps before/after recovering timestamps.
    """
    runForAllSensors(
        sensorId,
        lambda id: dataService.plotSensorInterval(id, recovered),
    )


@app.command()
def plotReceiveInterval(
    sensorId: str = "",
):
    """
    Plot interval between consecutive receive timestamps.
    """
    runForAllSensors(
        sensorId,
        lambda id: dataService.plotReceiveInterval(id),
    )


@app.command()
def plotRadon(
    sensorId: str = "",
    recovered: Annotated[bool, typer.Option("--recovered")] = False,
):
    """
    Plot radon histogram data before/after recovering timestamps.
    """
    runForAllSensors(
        sensorId,
        lambda id: dataService.plotRadon(id, recovered),
    )


def runForAllSensors(
    sensorId: str | None,
    task: Callable[[str], None],
):
    """
    If sensorId is missing run the task for all the sensors.
    """
    sensorIds = dataService.getAllSensors() if sensorId == "" else [sensorId]
    for sensorId in sensorIds:
        print(f"=============================== {sensorId} : {task.__qualname__}")
        task(sensorId)


if __name__ == "__main__":
    app()
